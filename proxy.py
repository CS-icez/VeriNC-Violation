from enum import Enum
import select
import string
import socket
import time
import threading
from typing import Callable

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

def delay_send(pkt: bytes, out_if: str, cond=None, callback=None):
    send_queue.append((pkt, out_if, cond, callback))
    log('INFO', f'[{rel_time_str()}]Scheduled delayed packet to {out_if}')


def deamon():
    while True:
        time.sleep(0.1)
        for idx, (pkt, out_if, cond, callback) in enumerate(send_queue):
            try:
                if cond is not None and not cond():
                    continue
                log('STATE', f'[{rel_time_str()}]Sending delayed packet to {out_if}: op={get_op_name(pkt)}')
                sockets[out_if].send(pkt)
                if callback is not None:
                    callback()
                send_queue.pop(idx)
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

def log_recv_pkt(pkt: bytes, in_if: str):
    log('RECV', f'[{rel_time_str()}]Packet received from {in_if}: op={get_op_name(pkt)}')
    # print_pkt(pkt)

def process_pkt(pkt: bytes, in_if: str):
    global start_time_ns
    if pkt[0] == 0x33 and pkt[1] == 0x33:
        # log('DROP', f'Dropping IPv6 multicast packet from {in_if}')
        return
    elif start_time_ns == -1:
        start_time_ns = time.time_ns()
    if in_if == 'veth-server0':
        process_server0(pkt, in_if)
    elif in_if == 'veth-client0':
        process_client0(pkt, in_if)
    elif in_if == 'veth-client1':
        process_client1(pkt, in_if)
    elif in_if == 'veth-tofino8':
        process_tofino8(pkt, in_if)
    else:
        log_recv_pkt(pkt, in_if)
        out_if = out_if_map[in_if]
        sockets[out_if].send(pkt)
        log('SEND', f'Forwarding packet from {in_if} to {out_if}')

class OpCode(Enum):
    PUTREQ                 = 0x0001
    PUTREQ_INSWITCH        = 0x0005
    PUTREQ_SEQ             = 0x0003
    PUTRES_SEQ             = 0x000a
    GETREQ                 = 0x0030
    GETREQ_INSWITCH        = 0x0004
    GETREQ_NLATEST         = 0x0060
    GETRES_LATEST_SEQ      = 0x000b
    GETRES_SEQ             = 0x006b
    WARMUPREQ              = 0x0000
    WARMUPACK              = 0x00d0
    SETVALID_INSWITCH      = 0x0054
    SETVALID_INSWITCH_ACK  = 0x0110
    CACHE_POP_INSWITCH     = 0x007f
    CACHE_POP_INSWITCH_ACK = 0x0070

def get_op(pkt: bytes) -> int:
    return (pkt[42] << 8) | pkt[43]

def is_op(pkt: bytes, op_code: OpCode) -> bool:
    return get_op(pkt) == op_code.value

def get_op_name(pkt: bytes) -> str:
    op = get_op(pkt)
    try:
        return OpCode(op).name
    except ValueError:
        return f'UNKNOWN_OP_{op:04x}'

# 0: Initial state.
# 1: First SETVALID_INSWITCH server0 -> switch.
# 2; PUTREQ client0 -> switch.
# 3: Second SETVALID_INSWITCH server0 -> switch. 
# 4: GETREQ client1 -> switch.
# 5: GETREQ_NLATEST switch -> server0.
# 6: PUTREQ_SEQ switch -> server0.
state = 0
setvalid_cnt = 0

def is_state_n(n: int) -> Callable[[], bool]:
    global state
    def f() -> bool:
        return state == n
    return f

def inc_state():
    global state
    state += 1
    log('STATE', f'[{rel_time_str()}]server0_state: {state - 1} -> {state}')

def process_client0(pkt: bytes, in_if: str):
    global state

    out_if = out_if_map[in_if]

    if is_op(pkt, OpCode.PUTREQ):
        log_recv_pkt(pkt, in_if)
        delay_send(pkt, out_if, is_state_n(1), inc_state)
        return
    
    log_recv_pkt(pkt, in_if)
    sockets[out_if].send(pkt)
    log('SEND', f'Forwarding packet from {in_if} to {out_if}')
    return

def process_client1(pkt: bytes, in_if: str):
    global state

    out_if = out_if_map[in_if]

    if is_op(pkt, OpCode.GETREQ):
        log_recv_pkt(pkt, in_if)
        delay_send(pkt, out_if, is_state_n(3), inc_state)
        return
    
    log_recv_pkt(pkt, in_if)
    sockets[out_if].send(pkt)
    log('SEND', f'Forwarding packet from {in_if} to {out_if}')
    return

def process_tofino8(pkt: bytes, in_if: str):
    global state

    out_if = out_if_map[in_if]

    if is_op(pkt, OpCode.GETREQ_NLATEST):
        log_recv_pkt(pkt, in_if)
        delay_send(pkt, out_if, is_state_n(4), inc_state)
        return
    
    if is_op(pkt, OpCode.PUTREQ_SEQ):
        log_recv_pkt(pkt, in_if)
        delay_send(pkt, out_if, is_state_n(5), inc_state)
        return
    
    log_recv_pkt(pkt, in_if)
    sockets[out_if].send(pkt)
    log('SEND', f'Forwarding packet from {in_if} to {out_if}')
    return

def process_server0(pkt: bytes, in_if: str):
    global state, setvalid_cnt

    out_if = out_if_map[in_if]

    if is_op(pkt, OpCode.SETVALID_INSWITCH):
        if setvalid_cnt == 0: # First.
            log_recv_pkt(pkt, in_if)
            delay_send(pkt, out_if, is_state_n(0), inc_state)
        elif setvalid_cnt == 1: # Second.
            log_recv_pkt(pkt, in_if)
            delay_send(pkt, out_if, is_state_n(2), inc_state)
        else:
            # log('DROP', f'Dropping retransmitted SETVALID_INSWITCH packet from {in_if}')
            pass
        setvalid_cnt += 1
        return

    log_recv_pkt(pkt, in_if)
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