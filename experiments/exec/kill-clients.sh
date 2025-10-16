#!/bin/bash

source ~/set-env.sh

echo $PASSWORD | sudo -S pkill -2 microbench > /dev/null 2>&1
echo $PASSWORD | sudo -S pkill -2 txnbench > /dev/null 2>&1
echo $PASSWORD | sudo -S pkill -2 server > /dev/null 2>&1
echo $PASSWORD | sudo -S pkill -2 redis_txn_ > /dev/null 2>&1
