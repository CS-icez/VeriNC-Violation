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

start_time_ns = -1
def rel_time_str():
    rel_time_us = (time.time_ns() - start_time_ns) // 1000 if start_time_ns != -1 else 0
    return f"{rel_time_us:09,}"


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
    print(f'[{rel_time_str()}]Packet received from {in_if}, length {len(pkt)} bytes:')
    print_pkt(pkt)
    # if in_if == 'veth-tofino0':
    #     process_tofino0(pkt, in_if)
    # else:
    out_if = out_if_map[in_if]
    sockets[out_if].send(pkt)
    print(f'Forwarding packet from {in_if} to {out_if}')

host1_state = 0 # before_release -> whatever

def is_release_reply(pkt: bytes) -> bool:
    return len(pkt) == 85 and pkt[43] == 0x06

def process_tofino0(pkt: bytes, in_if: str):
    global host1_state, start_time_ns

    out_if = out_if_map[in_if]

    if is_release_reply(pkt) and host1_state == 0:
        host1_state = 1
        print(f'[{rel_time_str()}]host1_state: 0 -> 1')
        print(f'Dropping release reply packet from {in_if}')
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