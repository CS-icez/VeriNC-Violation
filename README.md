# VeriNC Real System Violation Reproduction: FissLock

This repository is cloned from [FissLock's official repository](https://github.com/SJTU-IPADS/fisslock).

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

This process takes around 30 seconds.

## Run Experiment

Execute the following command to run the experiment:

```bash
sudo containerlab deploy; sudo containerlab destroy
```

This process takes around one minute.

## Result Analysis

In `log/violation.log`, you should see logs similar to the following:

```
[host1][Info][0000094]Client 1 attempts to acquire lock 343434 in exclusive mode
[host1][Info][1003402]Client 1 releases and re-acquires lock 343434 in exclusive mode after timeout
[host1][Info]Received POST_LOCK_GRANT_WITH_AGENT packet for lock 343434 from host 1 task 1
[host1][Info][1226083]Client 1 is granted with lock 343434 in exclusive mode
[host2][Info][1800141]Client 2 attempts to acquire lock 343434 in exclusive mode
[host2][Info]Received POST_LOCK_GRANT_WITH_AGENT packet for lock 343434 from host 2 task 2
[host2][Info][1820362]Client 2 is granted with lock 343434 in exclusive mode
```

Client 1 and Client 2 are granted the same exclusive lock at the same time, violating lock exclusion property.

You may refer to other log files in the `log/` directory for more detailed information.
