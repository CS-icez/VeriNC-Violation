# VeriNC Real System Violation Reproduction

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

## Clone Repository

Replace `<branch>` with one of `SwitchML` `ATP` `NetCache` `FarReach` `NetLock` `FissLock`, and run the following command:

```bash
git clone https://github.com/yourusername/verinc-violation.git -b <branch>
```

TODO: fill username.

## Run Experiment

Please follow the README file in the corresponding branch for detailed instructions on how to run the experiment for each system.
