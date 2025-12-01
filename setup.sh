#!/bin/bash

export PROJ_DIR=$(pwd)
echo "Project directory set to: $PROJ_DIR"
export TOFINO_PROJ_DIR="/root/$abc/atp"
echo "Tofino project directory set to: $TOFINO_PROJ_DIR"
export CS_PROJ_DIR="/root/atp"
echo "Client/Server project directory set to: $CS_PROJ_DIR"

function compile_p4() {
    docker run -it --rm -v $PROJ_DIR:$TOFINO_PROJ_DIR tofino:20251025 bash -ic " \
        bf-p4c --verbose 3 -g -x p4-14 -a tna -b tofino --program-name p4ml \
            -o $TOFINO_PROJ_DIR/p4-14-build $TOFINO_PROJ_DIR/p4src/p4ml.p4 \
    "
}

function compile_client_server() {
    docker run -it --rm -v $PROJ_DIR:$CS_PROJ_DIR --entrypoint bash dpdk:v21.11.4 \
        -c "make -C $CS_PROJ_DIR/client && make -C $CS_PROJ_DIR/server"
}
