## DPDK Transport (Kernel-bypass)

This repository uses DPDK for packet send/receive (userspace kernel-bypass). The legacy UDP socket fallback has been removed.

### Build

By default builds use DPDK:

```
make -C client DPDK=1
make -C server DPDK=1
```

Optionally, you can enable the original RDMA path (requires verbs libraries and device):

```
make -C client RDMA=1
make -C server RDMA=1
```

Provide DPDK EAL arguments via `DPDK_EAL_ARGS` and optionally choose the port with `DPDK_PORT_ID` (default 0). Example:

```
export DPDK_EAL_ARGS="-l 0-1 -n 4 --allow=0000:01:00.0"
export DPDK_PORT_ID=0
```

### Runtime Configuration

- `DPDK_EAL_ARGS`: DPDK EAL parameters (cores, mem channels, device allowlist, etc.)
- `DPDK_PORT_ID`: Port id to use for RX/TX (default 0)

### Differences vs RDMA

- DPDK: userspace NIC I/O with bursts; packets include L2/L3 header inline like RDMA; header offset (`P4ML_HEADER_OFFSET`) is 34.
- Loss/timeout logic remains, but timing characteristics differ.

### Notes

- Further tuning (batching, pacing, reliability) can be added incrementally without changing higher-level logic.

# ATP

ATP is a service that performs multi-rack multi-tenant in-network aggregation via co-designing with programmable switch and end-host networking stack.

# Benchmark
To run the benchmark, please see [benchmark](docs/benchmark.md).

# Publications

- [NSDI'21] "[ATP: In-network Aggregation for Multi-tenant Learning](https://www.usenix.org/conference/nsdi21/presentation/lao)". ChonLam Lao, Yanfang Le, Kshiteej Mahajan, Yixi Chen, Wenfei Wu, Aditya Akella, Michael Swift.

# Contact

Any questions? Please feel free to reach us at inatpcontact@gmail.com. You are more likely to receive a helpful response if your question is specific, self-contained and concise.
