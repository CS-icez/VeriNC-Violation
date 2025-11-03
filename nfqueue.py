from netfilterqueue import NetfilterQueue
from queue import PriorityQueue
import time
import threading

pq = PriorityQueue() # (send_time, packet)

def deamon():
    global host1_state
    while True:
        send_time, pkt = pq.get(block=True)
        if send_time <= time.perf_counter_ns():
            if pkt.get_payload() == host1_acquire and host1_state == 1:
                host1_state = 2
                print('host1_state: granting -> releasing')
            pkt.accept()

host1_acquire = bytes.fromhex('''
    4500 002d 0000 0000 0011 0000 0002 000a 0102 000a
    4e23 4e21 0019 0000
    0100 0005 3d8a 0101 0000 0001 0000 0000 00
''')
host1_release = bytes.fromhex('''
    4500 002d 0000 0000 0011 0000 0002 000a 0102 000a
    4e22 4e21 0019 0000
    0400 0005 3d8a 0101 0000 0001 0000 0000 00
''')
host1_state = 0 # acquiring -> granting -> releasing -> whatever

def process_host1(pkt):
    print('Get packet from host1')
    global host1_state
    payload = pkt.get_payload()

    if host1_state == 0 and payload == host1_acquire:
        host1_state = 1
        print('host1_state: acquiring -> granting')
        send_time = time.perf_counter_ns() + 11_000_000
        pq.put((send_time, pkt))
        return
    
    if host1_state == 1 and payload == host1_release:
        while host1_state == 1:
            pass
    
    if host1_state == 2 and payload == host1_release:
        host1_state = 3
        print('host1_state: releasing -> whatever')
        pkt.accept()
        return

    pkt.drop()
    return

host2_acquire = bytes.fromhex('''
    4500 002d 0000 0000 0011 0000 0002 000a 0102 000a
    4e25 4e21 0019 0000               
    0100 0005 3d8a 0202 0000 0002 0000 0000 00
''')
host2_state = 0 # acquiring -> whatever

def process_host2(pkt):
    print('Get packet from host2')
    global host2_state
    payload = pkt.get_payload()
    
    if host2_state == 0 and payload == host2_acquire:
        host2_state = 1
        print('host2_state: acquiring -> whatever')
        send_time = time.perf_counter_ns() + 15_000_000
        pq.put((send_time, pkt))
        return

    pkt.drop()
    return

def run_nfqueue(num, handler):
    nfq = NetfilterQueue()
    nfq.bind(num, handler)
    print(f'NFQUEUE {num} running...')
    nfq.run() # No unbinding, but okay for its purpose.

threading.Thread(target=deamon, daemon=True).start()
threading.Thread(target=run_nfqueue, args=(1, process_host1), daemon=True).start()
threading.Thread(target=run_nfqueue, args=(2, process_host2), daemon=True).start()

try:
    threading.Event().wait() # Wait forever.
except KeyboardInterrupt:
    print('\nExit without unbinding NFQUEUEs.')
