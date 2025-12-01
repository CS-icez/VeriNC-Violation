## Socket Fallback (No RDMA)

This repository originally depended on RDMA (libibverbs/rdmacm) for packet send/receive. A minimal UDP socket fallback has been added so experiments can run inside container networks without RDMA hardware or kernel modules.

### Build

By default RDMA is disabled and the socket transport is used:

```
make -C client
make -C server
```

To enable the original RDMA path (requires verbs libraries and device):

```
make -C client RDMA=1
make -C server RDMA=1
```

### Runtime Configuration (Socket Mode)

Environment variables allow basic addressing without code changes:

- `P4ML_SERVER_IP`: IP address of the parameter server (set in client containers)
- `P4ML_CLIENT_IP`: IP address of a client (set in server container if needed for replies)
- `P4ML_BASE_PORT`: Base UDP port (default 6000). Each thread uses `base + thread_id`.

Example (single client and server on same host/network):

```
export P4ML_SERVER_IP=10.0.0.5
export P4ML_BASE_PORT=7000
make -C server &
make -C client
```

### Differences vs RDMA

- No flow rules, CQE snapshots, or zero-copy—simple datagram send/recv.
- Packet header offset (`P4ML_HEADER_OFFSET`) becomes 0 in socket mode.
- Loss/timeout logic remains, but timing characteristics differ.

### Notes

- The fallback focuses on compilation and functional API compatibility, not performance parity.
- Further tuning (batching, pacing, reliability) can be added incrementally without changing higher-level logic.
# ATP

ATP is a service that performs multi-rack multi-tenant in-network aggregation via co-designing with programmable switch and end-host networking stack.

# Benchmark
To run the benchmark, please see [benchmark](docs/benchmark.md).

# Publications

- [NSDI'21] "[ATP: In-network Aggregation for Multi-tenant Learning](https://www.usenix.org/conference/nsdi21/presentation/lao)". ChonLam Lao, Yanfang Le, Kshiteej Mahajan, Yixi Chen, Wenfei Wu, Aditya Akella, Michael Swift.

# Contact

Any questions? Please feel free to reach us at inatpcontact@gmail.com. You are more likely to receive a helpful response if your question is specific, self-contained and concise.
