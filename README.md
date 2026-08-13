# VeriNC Real System Violation Reproduction

**VeriNC** is the first general-purpose tool for verifying [in-network computing (INC)](https://en.wikipedia.org/wiki/In-network_computing) systems. By modeling INC protocols and performing model checking, VeriNC identifies design risks that can lead to property violations under network exceptions such as packet loss and out-of-order delivery.

This repository contains the code and instructions to **reproduce the violations** identified by VeriNC in six real INC system implementations. Each system is deployed in Docker containers with a proxy-based fault injection mechanism, enabling controlled reproduction of violation traces reported by VeriNC.

> 📄 **Paper:** Tianyu Bai, Xiaoxi Zhang, Haoqing Wang, Ying Zhang, Wenfei Wu. *VeriNC: Finding Design Risks of In-Network Computing Systems.* IEEE ICNP 2026. [[arXiv]](https://arxiv.org/abs/2604.10186)
>
> <!-- TODO: Add BibTeX citation when available -->

## Identified Violations

VeriNC identified property violations in seven INC systems across three application domains. We reproduced the violations in the six open-source systems listed below:

| System | Domain | Network | Violation | Explanation |
|--------|--------|---------|-----------|-------------|
| [SwitchML](https://github.com/p4lang/p4app-switchML) | Tensor Aggregation | out-of-order | computational correctness | Out-of-order breaks the assumption that completed requests will not reappear |
| [ATP](https://github.com/in-ATP/ATP) | Tensor Aggregation | out-of-order | memory leak freedom | A late request permanently occupies an aggregator after aggregation completes |
| [NetCache](https://github.com/netcache-p4/netcache-p4) | Key-Value Cache | lossy | cache consistency | Packet loss exposes the risk of replying to the client and updating the switch simultaneously |
| [NetCache](https://github.com/netcache-p4/netcache-p4) | Key-Value Cache | reliable | terminality | Cache eviction during a write leads to a state inconsistency |
| [FarReach](https://github.com/farreach-public/farreach-public) | Key-Value Cache | reliable | cache consistency | Event interleaving breaks the assumption that read replies carry the latest values |
| [NetLock](https://github.com/netx-repo/NetLock) | Lock Management | delayed | lock exclusion | Retransmitted release requests cause extra dequeuing on the switch |
| [FissLock](https://github.com/netx-repo/FissLock) | Lock Management | delayed | lock exclusion | Delayed acquisition triggers release and re-acquisition, causing inconsistent lock states |

## Reproduction Approach

Each system node (clients, programmable switches, servers) is deployed inside individual Docker containers. An additional **proxy node** is introduced to forward and manipulate network traffic among nodes. The proxy connects to all other nodes via virtual Ethernet pairs, preserving original system behavior while allowing controlled injection of:

- **Packet loss** — to trigger violations under lossy networks
- **Packet delay** — to trigger violations under delayed/out-of-order networks

The container topology is orchestrated using [Containerlab](https://containerlab.dev/). Following the violation traces reported by VeriNC, we inject faults through the proxy node and confirm violations by analyzing system logs.

## Prerequisites

### Docker

Install Docker from [here](https://www.docker.com/get-started), or use the one-click method:

```bash
curl -fsSL https://get.docker.com | sudo bash
```

### Barefoot SDE

A Docker image with **Barefoot SDE** installed is required. Barefoot SDE is not publicly available — please obtain it from Intel.

This project is tested with Barefoot SDE version **9.7.0**.

### Containerlab

Install Containerlab from [here](https://containerlab.dev/install/), or use the one-click method:

```bash
bash -c "$(curl -sL https://get.containerlab.dev)"
```

### Huge Pages

Barefoot SDE requires hugetlbfs to run `switchd`. Refer to the [hugetlbfs documentation](https://www.kernel.org/doc/Documentation/vm/hugetlbpage.txt) for details.

Mount hugetlbfs on your host machine at `/dev/hugepages`. **128 × 2 MB** is sufficient for all experiments.

## Getting Started

Each system's reproduction code is maintained on a **separate branch**. Clone the repository and check out the branch corresponding to the system you want to reproduce:

```bash
git clone https://github.com/CS-icez/VeriNC-Violation.git -b <branch>
```

Replace `<branch>` with one of the following:

| Branch | System | Domain |
|--------|--------|--------|
| `SwitchML` | SwitchML | Tensor Aggregation |
| `ATP` | ATP | Tensor Aggregation |
| `NetCache` | NetCache | Key-Value Cache |
| `FarReach` | FarReach | Key-Value Cache |
| `NetLock` | NetLock | Lock Management |
| `FissLock` | FissLock | Lock Management |

Then follow the **README** in the checked-out branch for detailed instructions on building, deploying, and running the reproduction experiment.

## Repository Structure

```
VeriNC-Violation/
├── main                # This landing page
├── SwitchML            # Branch: SwitchML reproduction
├── ATP                 # Branch: ATP reproduction
├── NetCache            # Branch: NetCache reproduction
├── FarReach            # Branch: FarReach reproduction
├── NetLock             # Branch: NetLock reproduction
└── FissLock            # Branch: FissLock reproduction
```

Each branch typically contains:
- **Containerlab topology** definition for the system
- **Dockerfile(s)** for building system nodes and the proxy
- **Proxy scripts** for fault injection (packet loss/delay)
- **Run scripts** for one-click experiment execution
- **Analysis scripts** for log inspection and violation confirmation

## Related Repositories

- [VeriNC Compiler](https://github.com/CS-icez/VeriNC-Compiler) — Compiler that translates `.inc` protocol specifications into TLA+/PlusCal for model checking.
- [EPIC](https://github.com/In-Net/EPIC) — An INC protocol specification and reference system built on the principle of "Unified Abstraction, Polymorphic Realization" (SIGCOMM 2026), which uses VeriNC for formal correctness verification.

## Citation

<!-- TODO: BibTeX entry will be added once the official citation is available. -->

If you use this work in your research, please cite:

> Tianyu Bai, Xiaoxi Zhang, Haoqing Wang, Ying Zhang, Wenfei Wu. "VeriNC: Finding Design Risks of In-Network Computing Systems." IEEE ICNP, 2026.
