import select
import string
import socket
import queue
import time
import threading

veth_pairs = [
    ('veth-worker1', 'veth-tofino0'),
    ('veth-worker2', 'veth-tofino4'),
    ('veth-tofino68', 'veth-tofino68'),
]

out_if_map = {}
for if1, if2 in veth_pairs:
    out_if_map[if1] = if2
    out_if_map[if2] = if1

sockets = {}  # if_name -> socket.socket
send_queue = queue.PriorityQueue()  # (send_time, pkt, out_if, callback)

start_time_ns = -1
def rel_time_str():
    rel_time_us = (time.time_ns() - start_time_ns) // 1000 if start_time_ns != -1 else 0
    return f"{rel_time_us:09,}"

def delay_send(pkt: bytes, out_if: str, delay_ns: int, callback=None):
    send_time = time.time_ns() + delay_ns
    send_queue.put((send_time, pkt, out_if, callback))


def deamon():
    while True:
        send_time, pkt, out_if, callback = send_queue.get(block=True)
        now = time.time_ns()
        if send_time > now:
            time.sleep((send_time - now) / 1e9)
        try:
            print(f'[{rel_time_str()}]Sending delayed packet to {out_if}, pkt_id={pkt[44]}')
            sockets[out_if].send(pkt)
            if callback:
                callback()
        except Exception as e:
            print(f"Error sending packet to {out_if}: {e}")


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
        print(line)


def process_pkt(pkt: bytes, in_if: str):
    global start_time_ns
    if pkt[0] == 0x33 and pkt[1] == 0x33:
        # IPv6 multicast packet, drop it
        # print(f'Dropping IPv6 multicast packet from {in_if}')
        return
    elif start_time_ns == -1:
        start_time_ns = time.time_ns()
    print(f'[{rel_time_str()}]Packet received from {in_if}, pkt_id={pkt[44]}:')
    # print_pkt(pkt)
    if in_if == 'veth-worker1':
        process_worker1(pkt, in_if)
    elif in_if == 'veth-worker2':
        process_worker2(pkt, in_if)
    else:
        out_if = out_if_map[in_if]
        sockets[out_if].send(pkt)
        print(f'Forwarding packet from {in_if} to {out_if}')

host1_state = 0 # first_request -> whatever

def is_request(pkt: bytes) -> bool:
    return len(pkt) == 308 and pkt[42] == 0x11

def process_worker1(pkt: bytes, in_if: str):
    global host1_state

    out_if = out_if_map[in_if]

    if is_request(pkt) and host1_state == 0:
        if pkt[44] != 0x00:
            print(f'[{rel_time_str()}]Unexpected request packet from {in_if}: host1_state=0 but non-first request')
            return
        host1_state = 1
        print(f'[{rel_time_str()}]host1_state: 0 -> 1')
        delay_send(pkt, out_if, 1_500_000_000)
        return
    
    if is_request(pkt) and host1_state == 1 and pkt[44] == 0x02:
        print(f'[{rel_time_str()}]Dropping third request packet from {in_if}')
        return

    sockets[out_if].send(pkt)
    print(f'Forwarding packet from {in_if} to {out_if}')
    return

host2_state = 0 # third_request -> whatever

def process_worker2(pkt: bytes, in_if: str):
    global host2_state

    out_if = out_if_map[in_if]

    if is_request(pkt) and host2_state == 0 and pkt[44] == 0x02:
        host2_state = 1
        print(f'[{rel_time_str()}]host2_state: 0 -> 1')
        delay_send(pkt, out_if, 700_000_000)
        return

    sockets[out_if].send(pkt)
    print(f'Forwarding packet from {in_if} to {out_if}')
    return


def create_raw_socket(if_name: str) -> socket.socket:
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(3))
    s.bind((if_name, 0))
    return s


if __name__ == "__main__":
    for if1, if2 in veth_pairs:
        sockets[if1] = create_raw_socket(if1)
        sockets[if2] = create_raw_socket(if2)
        print(f'Created raw sockets for {if1} and {if2}')

    threading.Thread(target=deamon, daemon=True).start()
    print('Daemon thread started.')

    print('Starting main loop to process packets...')
    try:
        while True:
            rlist, _, _ = select.select(sockets.values(), [], [])
            for s in rlist:
                in_if = s.getsockname()[0]
                pkt, _ = s.recvfrom(65535)
                process_pkt(pkt, in_if)
    except KeyboardInterrupt:
        print('Exiting on user interrupt...')
        for s in sockets.values():
            s.close()
        print('Sockets closed. Goodbye!')