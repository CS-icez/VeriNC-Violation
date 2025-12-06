# VeriNC Real System Violation Reproduction: ATP

This repository is cloned from [ATP's official repository](https://github.com/in-ATP/ATP/tree/experimental_p416).

## Prequisites

Please first refer to the README file of the main branch for general instructions about this project.

## Build Docker Image

Make sure you are in the root directory of this repository and run:

```bash
docker build -t dpdk:v21.11.4 -f dpdk-v21.11.4.Dockerfile .
```

## Setup

Replace `<sde_name>` with the name of the Docker image of Barefoot SDE (e.g., `sde:9.7.0`) and run:

```bash
bash project_setup.sh <sde_name>
```

This process takes around one minute.

## Run Experiment

Execute the following command to run the experiment:

```bash
sudo containerlab deploy; sudo containerlab destroy
```

This process takes around 90 seconds.

## Result Analysis

Sorry we are not able to provide a direct evidence of the memory leak freedom violation in ATP, due to a bug in Barefoot SDE register dump. Yet, with deep understanding of the data plane of ATP, you will be able to inference the violation from the log files in `log/`.

## Network Timing Diagram

![Network Timing Diagram](timing.svg)
