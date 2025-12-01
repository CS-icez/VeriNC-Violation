#!/bin/bash

export PROJ_DIR=$(pwd)
echo "Project directory set to: $PROJ_DIR"
export PROJ_NAME=$(basename $PROJ_DIR)
echo "Project name set to: $PROJ_NAME"
export TOFINO_PROJ_DIR="/root/$abc/$PROJ_NAME"
echo "Tofino project directory set to: $TOFINO_PROJ_DIR"

function upload_to_tofino() {
    local remote_dir="/root/$abc/$PROJ_NAME"
    echo "Uploading project to Tofino at $remote_dir"
    rsync -a --delete --exclude='.git' $PROJ_DIR/ tofino:$remote_dir/
}

function upload_to_worker() {
    if [ -z "$1" ]; then
        echo "Usage: upload_to_worker <worker_id1> ..."
        return 1
    fi
    for worker_id in "$@"; do
        echo "Uploading project to Worker $worker_id at $TOFINO_PROJ_DIR"
        rsync -a --delete --exclude='.git' $PROJ_DIR/ worker$worker_id:$TOFINO_PROJ_DIR/
    done
}

function compile_p4() {
    docker run -it --rm -v $PROJ_DIR:$TOFINO_PROJ_DIR tofino:20251025 bash -ic " \
        bf-p4c --verbose 3 -g -a tna -b tofino --program-name p4ml16 \
            -o $TOFINO_PROJ_DIR/p4-build $TOFINO_PROJ_DIR/atp-p4-16/main.p4 \
    "
}
