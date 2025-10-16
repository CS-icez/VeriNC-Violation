machines = [
    {'name': "worker1", 'ip': 0xc0a80101, 'mac': 0x1070fd190095, 'port': 128},
    {'name': "worker2", 'ip': 0xc0a80102, 'mac': 0x1070fd2fd851, 'port': 144},
    {'name': "worker3", 'ip': 0xc0a80103, 'mac': 0x1070fd2fe441, 'port': 160},
    {'name': "worker4", 'ip': 0xc0a80104, 'mac': 0x1070fd2fd421, 'port': 176}
]

pipe = bfrt.fisslock_decider.pipe.IngressPipe

for m in machines:
    pipe.eth_fallback.add_with_eth_forward(
        dst_mac=m['mac'],
        port=m['port']
    )
