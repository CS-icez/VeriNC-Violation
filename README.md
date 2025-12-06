# VeriNC Real System Violation Reproduction: SwitchML

This repository is cloned from [SwitchML's official repository](https://github.com/p4lang/p4app-switchML).

## Prequisites

Please first refer to the README file of the main branch for general instructions about this project.

## Clone Submodule

```bash
git submodule update --init --recursive
```

## Build Docker Image

Make sure you are in the root directory of this repository and run:

```bash
docker build -t dpdk:v21.11.4 -f dpdk-v21.11.4.Dockerfile .
docker build -t switchml-client:latest -f dev_root/dockerfiles/dpdk.dockerfile .
```

Replace the `tofino:20251025` on the first line of `switchml-tofino.Dockerfile` with the Docker image of Barefoot SDE you are using (e.g., `sde:9.7.0`), then run:

```bash
docker build -t switchml-tofino:latest -f switchml-tofino.Dockerfile .
```

## Setup

You need to modify the `GRPC_HOME` on line 57 of `project_setup.sh` such that `$GRPC_HOME/bin/protoc` exists.

Replace `<sde_name>` with the name of the Docker image of Barefoot SDE (e.g., `sde:9.7.0`) and run:

```bash
bash project_setup.sh <sde_name>
```

This process takes around two minutes.

## Run Experiment

Execute the following command to run the experiment:

```bash
sudo containerlab deploy; sudo containerlab destroy
```

This process takes around one minute.

## Result Analysis

In `log/violation_worker1.log`, you should see logs similar to the following:

```
Failed to verify output data. Element 128 in tensor 0 was 128 but we expected 256
```

Worker 1 detects incorrect results, i.e., a violation of computational correctness.

You may refer to other log files in the `log/` directory for more detailed information.

## Network Timing Diagram

![Network Timing Diagram](timing.svg)
