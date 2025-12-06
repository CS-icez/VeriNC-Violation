# VeriNC Real System Violation Reproduction: FissLock

This repository is cloned from [FissLock's official repository](https://github.com/SJTU-IPADS/fisslock). We use the NetLock reproduced by FissLock because the original FissLock implementation is based on P4-14 and is not compatible with the latest Barefoot SDE.

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

This process takes around one minute.

## Result Analysis

In `log/violation.log`, you should see logs similar to the following:

```
[host2][Info][0000152]Client 2 attempts to acquire lock 34 in shared mode
[host2][Info][0019916]Client 2 is granted with lock 34 in shared mode
[host1][Info][0000092]Client 1 attempts to acquire lock 34 in shared mode
[host1][Info][0009849]Client 1 is granted with lock 34 in shared mode
[host3][Info][0500333]Client 3 attempts to acquire lock 34 in exclusive mode
[host1][Info][1009968]Client 1 attempts to release lock 34 in shared mode
[host1][Info][2010398]Client 1 releases lock 34 again in shared mode after timeout
[host1][Info][2032226]Client 1 is acknowledged as having released lock 34
[host3][Info][2059572]Client 3 is granted with lock 34 in exclusive mode
```

Client 2 and Client 3 are granted the same exclusive lock at the same time, violating lock exclusion property.

You may refer to other log files in the `log/` directory for more detailed information.
