import select
import string
import socket
import queue
import time
import threading

veth_pairs = [
    ('veth-worker1', 'veth-tofino128'),
    ('veth-worker2', 'veth-tofino144'),
    ('veth-worker3', 'veth-tofino160'),
    ('veth-worker4', 'veth-tofino176'),
    ('veth-tofino188', 'veth-tofino188'),  # Loopback port.
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
            print(f'[{rel_time_str()}]Sending delayed packet to {out_if}, length {len(pkt)} bytes')
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
        print(f'Dropping IPv6 multicast packet from {in_if}')
        return
    elif start_time_ns == -1:
        start_time_ns = time.time_ns()
    print(f'[{rel_time_str()}]Packet received from {in_if}:')
    print_pkt(pkt)
    # if in_if == 'veth-worker1':
    #     process_worker1(pkt, in_if)
    # elif in_if == 'veth-worker2':
    #     process_worker2(pkt, in_if)
    # else:
    out_if = out_if_map[in_if]
    sockets[out_if].send(pkt)
    print(f'Forwarding packet from {in_if} to {out_if}')

host1_acquire = bytes.fromhex('''
    08c0 ebdc a112 08c0 ebdc b300 0800 4500
    002d 0000 0000 0011 0000 0002 000a 0102 
    000a 4e00 4e21 0019 0000 0101 0005 3d8a
    0101 0000 0001 0000 0000 00
''')
host1_release = bytes.fromhex('''
    08c0 ebdc a112 08c0 ebdc b300 0800 4500
    002d 0000 0000 0011 0000 0002 000a 0102
    000a 4e00 4e21 0019 0000 0400 0005 3d8a
    0101 0000 0001 0000 0000 00
''')
host2_acquire = bytes.fromhex('''
    08c0 ebdc a112 08c0 ebdc b300 0800 4500
    002d 0000 0000 0011 0000 0002 000a 0102              
    000a 4e00 4e21 0019 0000 0101 0005 3d8a
    0202 0000 0002 0000 0000 00
''')
lock_mask = bytes.fromhex('''
    ffff ffff ffff ffff ffff ffff ffff ffff
    ffff ffff ffff ffff ffff ffff ffff ffff
    ffff ff00 ffff ffff ffff ffff ffff ffff
    ffff ffff ffff ffff ffff ff
''')
host1_state = 0
host2_state = 0 # acquiring -> whatever

def pkt_eq(pkt1: bytes, pkt2: bytes, mask: bytes) -> bool:
    if not (len(pkt1) == len(pkt2) == len(mask)):
        return False
    return all((b1 & m) == (b2 & m) for b1, b2, m in zip(pkt1, pkt2, mask))

def process_worker1(pkt: bytes, in_if: str):
    global host1_state, start_time_ns

    out_if = out_if_map[in_if]

    def cb_acquire():
        global host1_state
        print(f'[{rel_time_str()}]host1_state: {host1_state} -> 3')
        host1_state = 3
        return

    if pkt_eq(pkt, host1_acquire, lock_mask):
        if host1_state != 0:
            print(f'Dropping acquire packet from worker1: host1_state={host1_state}')
            return
        start_time_ns = time.time_ns()
        host1_state = 1
        print(f'[{rel_time_str()}]host1_state: 0 -> 1')
        delay_send(host1_acquire, out_if, 1_200_000_000, cb_acquire)
        return

    def cb_release():
        global host1_state
        print(f'[{rel_time_str()}]host1_state: {host1_state} -> 4')
        host1_state = 4

    if pkt_eq(pkt, host1_release, lock_mask):
        if host1_state != 1:
            print(f'Dropping release packet from worker1: host1_state={host1_state}')
            return
        print(f'[{rel_time_str()}]host1_state: 1 -> 2')
        host1_state = 2
        delay_send(pkt, out_if, 500_000_000, cb_release)
        return

    print('Dropping packet from worker1')
    return

def process_worker2(pkt: bytes, in_if: str):
    global host2_state

    out_if = out_if_map[in_if]

    if pkt_eq(pkt, host2_acquire, lock_mask):
        if host2_state != 0:
            print(f'Dropping acquire packet from worker2: host2_state={host2_state}')
            return
        host2_state = 1
        print(f'[{rel_time_str()}]host2_state: 0 -> 1')
        sockets[out_if].send(pkt)
        return

    # print('Dropping packet from worker2')
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