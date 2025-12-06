# VeriNC Real System Violation Reproduction

VeriNC is a general-purpose INC (In-Network Computing) system verification tool, allowing users to model INC systems and verify correctness properties.

This repository contains the code and instructions to reproduce violations for six INC systems.

## Prerequisites

### Docker

You can install Docker from [here](https://www.docker.com/get-started). The following is a possible one-click installation method:

```bash
curl -fsSL https://get.docker.com | sudo bash
```

### Barefoot SDE

You need a docker image with Barefoot SDE installed, which is not publicly available. Please obtain it from Intel.

This project is tested with Barefoot SDE version 9.7.0.

### Containerlab

This project replies on Containerlab to orchestrate the containerized network.

You can install Containerlab from [here](https://containerlab.dev/install/). The following is a possible one-click installation method:

```bash
bash -c "$(curl -sL https://get.containerlab.dev)"
```

### Huge Page

Barefoot SDE requires hugetlbfs to run switchd. You may refer to [this document](https://www.kernel.org/doc/Documentation/vm/hugetlbpage.txt) for more information about hugetlbfs.

You must mount hugetlbfs on your host machine at `/dev/hugepages`. 128*2MB is enough for all experiments.

## Clone Repository

Replace `<branch>` with one of `SwitchML` `ATP` `NetCache` `FarReach` `NetLock` `FissLock`, and run the following command:

```bash
git clone https://github.com/yourusername/verinc-violation.git -b <branch>
```

TODO: fill username.

## Next

Please follow the README file in the corresponding branch for detailed instructions on how to run the experiment for each system.
