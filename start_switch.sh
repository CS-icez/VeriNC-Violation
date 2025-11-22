#!/bin/bash

if [ $# -ne 1 ]
then
    echo "Usage: $0 <program_name>"
    exit 1
fi

set -x
program_name=$1
$SDE/run_tofino_model.sh -f ports.json -p $program_name &> $PROJ_DIR/log/tofino_model.log &
sleep 10
$SDE/run_switchd.sh -p $program_name &> $PROJ_DIR/log/switchd.log
