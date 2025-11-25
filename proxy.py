import select
import string
import socket
import queue
import time
import threading
import sys

veth_pairs = [
    ('veth-client0', 'veth-tofino0'),
    ('veth-client1', 'veth-tofino4'),
    ('veth-server0', 'veth-tofino8'),
    ('veth-server1', 'veth-tofino12'),
    ('veth-tofino16', 'veth-tofino144'),
]

out_if_map = {}
for if1, if2 in veth_pairs:
    out_if_map[if1] = if2
    out_if_map[if2] = if1

sockets = {}  # if_name -> socket.socket
send_queue = []  # (send_time, pkt, out_if, condition)

start_time_ns = -1
def rel_time_str():
    rel_time_us = (time.time_ns() - start_time_ns) // 1000 if start_time_ns != -1 else 0
    return f"{rel_time_us:09,}"

def delay_send(pkt: bytes, out_if: str, delay_ns: int, cond=None):
    send_time = time.time_ns() + delay_ns
    send_queue.append((send_time, pkt, out_if, cond))
    log('INFO', f'[{rel_time_str()}]Scheduled delayed packet to {out_if} in {delay_ns / 1e9:.3f}s')


def deamon():
    while True:
        while not send_queue:
            time.sleep(1)
        send_time, pkt, out_if, cond = send_queue.pop(0)
        now = time.time_ns()
        if send_time > now:
            time.sleep((send_time - now) / 1e9)
        try:
            log('SEND', f'[{rel_time_str()}]Sending delayed packet to {out_if}')
            if cond is not None:
                while not cond():
                    time.sleep(1)
            sockets[out_if].send(pkt)
        except Exception as e:
            log('ERROR', f"Error sending packet to {out_if}: {e}")


def print_pkt(pkt: bytes):
    for off in range(0, len(pkt), 16):
        line_len = min(16, len(pkt) - off)
        line = f"0x{off:04x}:  "
        for i in range(0, 16, 2):
            if i + 1 < line_len:
                line += f"{pkt[off + i]:02x}{pkt[off + i + 1]:02x} "
            elif i < line_len:
                line += f"{pkt[off + i]:02x}   "
            else:
                line += "     "
        line += " "
        ascii_part = ""
        for i in range(line_len):
            c = pkt[off + i]
            ascii_part += chr(c) if chr(c) in string.printable and c >= 0x20 else '.'
        line += ascii_part
        log('DEBUG', line)


def process_pkt(pkt: bytes, in_if: str):
    global start_time_ns
    if pkt[0] == 0x33 and pkt[1] == 0x33:
        log('DROP', f'Dropping IPv6 multicast packet from {in_if}')
        return
    elif start_time_ns == -1:
        start_time_ns = time.time_ns()
    log('RECV', f'[{rel_time_str()}]Packet received from {in_if}:')
    print_pkt(pkt)
    if in_if == 'veth-server0':
        process_server0(pkt, in_if)
    else:
        out_if = out_if_map[in_if]
        sockets[out_if].send(pkt)
        log('SEND', f'Forwarding packet from {in_if} to {out_if}')

PUTREQ            = 0x0001
GETREQ            = 0x0030
SETVALID_INSWITCH = 0x0054
WARMUPACK         = 0x00d0

def get_op(pkt: bytes) -> int:
    return (pkt[42] << 8) | pkt[43]

#    first SETVALID_INSWITCH 
# -> second SETVALID_INSWITCH
# -> first read
server0_state = 0 

def process_server0(pkt: bytes, in_if: str):
    global server0_state

    out_if = out_if_map[in_if]

    if get_op(pkt) == SETVALID_INSWITCH and server0_state == 0:
        server0_state = 1
        log('STATE', f'[{rel_time_str()}]server0_state: 0 -> 1')
        sockets[out_if].send(pkt)
        log('SEND', f'Forwarding packet from {in_if} to {out_if}')
        return

    def cond():
        global server0_state
        return server0_state == 5

    if get_op(pkt) == SETVALID_INSWITCH and server0_state == 1:
        server0_state = 2
        log('STATE', f'[{rel_time_str()}]server0_state: 1 -> 2')
        delay_send(pkt, out_if, 1_000_000_000)
        return
    
    if get_op(pkt) == SETVALID_INSWITCH and server0_state > 1:
        log('DROP', f'Dropping retransmitted SETVALID_INSWITCH packet from {in_if}')
        return
    
    if get_op(pkt) == PUTREQ: # TODO: not this
        if server0_state == 2:
            server0_state = 4
            log('STATE', f'[{rel_time_str()}]server0_state: 2 -> 4')
            delay_send(pkt, out_if, 1_000_000_000)
            return
        elif server0_state == 3:
            server0_state = 5
            log('STATE', f'[{rel_time_str()}]server0_state: 3 -> 5')
            delay_send(pkt, out_if, 1_000_000_000)
            return
    
    if get_op(pkt) == GETREQ: # TODO: not this
        if server0_state == 2:
            server0_state = 3
            log('STATE', f'[{rel_time_str()}]server0_state: 2 -> 3')
            delay_send(pkt, out_if, 1_000_000_000)
            return
        elif server0_state == 4:
            server0_state = 5
            log('STATE', f'[{rel_time_str()}]server0_state: 4 -> 5')
            send_queue.insert(0, (time.time_ns(), pkt, out_if, None))
            log('INFO', f'[{rel_time_str()}]Scheduled delayed packet to {out_if} in 0s')
            return

    sockets[out_if].send(pkt)
    log('SEND', f'Forwarding packet from {in_if} to {out_if}')
    return

def create_raw_socket(if_name: str) -> socket.socket:
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(3))
    s.bind((if_name, 0))
    return s


# Color / logging utilities
# COLOR_ENABLED = sys.stdout.isatty()
COLOR_ENABLED = True
RESET = '\033[0m' if COLOR_ENABLED else ''
COLORS = {
    'RECV': '\033[32m',
    'SEND': '\033[34m',
    'DROP': '\033[33m',
    'ERROR': '\033[31m',
    'STATE': '\033[35m',
    'START': '\033[36m',
    'EXIT': '\033[91m',
    'WARN': '\033[93m',
    'DEBUG': '\033[90m',
    'INFO': '\033[37m',
}
def log(kind: str, msg: str):
    c = COLORS.get(kind, '')
    if not COLOR_ENABLED:
        print(msg)
    else:
        print(f"{c}{msg}{RESET}")


if __name__ == "__main__":
    for if1, if2 in veth_pairs:
        sockets[if1] = create_raw_socket(if1)
        sockets[if2] = create_raw_socket(if2)
        log('START', f'Created raw sockets for {if1} and {if2}')

    threading.Thread(target=deamon, daemon=True).start()
    log('START', 'Daemon thread started.')
    log('INFO', 'Starting main loop to process packets...')
    try:
        while True:
            rlist, _, _ = select.select(sockets.values(), [], [])
            for s in rlist:
                in_if = s.getsockname()[0]
                pkt, _ = s.recvfrom(65535)
                process_pkt(pkt, in_if)
    except KeyboardInterrupt:
        log('EXIT', 'Exiting on user interrupt...')
        for s in sockets.values():
            s.close()
        log('EXIT', 'Sockets closed. Goodbye!')