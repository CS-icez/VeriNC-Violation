# VeriNC Real System Violation Reproduction: NetCache

This repository is cloned from [FarReach's official repository](https://github.com/LGN520/farreach-public). We use the NetCache reproduced by FarReach because the original NetCache implementation is based on P4-14 and is not compatible with the latest Barefoot SDE.

## Prequisites

Please first refer to the README file of the main branch for general instructions about this project.

## Build Docker Image

Make sure you are in the root directory of this repository and run:

```bash
docker build -t dpdk:v21.11.4 -f dpdk-v21.11.4.Dockerfile .
docker build -t netcache-client-server:latest -f client-server.dockerfile .
```

Replace the `tofino:20251025` on the first line of `tofino.dockerfile` with the Docker image of Barefoot SDE you are using (e.g., `sde:9.7.0`), then run:

```bash
docker build -t netcache-tofino:latest -f netcache-tofino.dockerfile .
```

## Setup

Replace `<sde_name>` with the name of the Docker image of Barefoot SDE (e.g., `sde:9.7.0`) and run:

```bash
bash project_setup.sh <sde_name>
```

This process takes around 70 seconds.

## Run Experiment

Execute the following command to run the experiment:

```bash
sudo containerlab deploy; sudo containerlab destroy
```

This process takes around 3 minutes.

## Result Analysis

In `log/violation.log`, you should see logs similar to the following:

```
[46547524354294][NetcacheClient][SEND][UPDATE] key=user1 value=332574265c632d28
[46547555752062][NetcacheClient][RECV][UPDATE] key=user1 value=332574265c632d28
[46547557660660][NetcacheClient][SEND][UPDATE] key=user1 value=224f3b215433333e
[46547580070133][NetcacheClient][RECV][UPDATE] key=user1 value=224f3b215433333e
[46547580275259][NetcacheClient][SEND][READ] key=user1
[46547747896478][NetcacheClient][RECV][READ] key=user1 value=332574265c632d28
```

The UPDATE has terminated but the next READ does not obtain the latest value, violating cache consistency.

You may refer to other log files in the `log/` directory for more detailed information.

## Network Timing Diagram

![Network Timing Diagram](timing.svg)
