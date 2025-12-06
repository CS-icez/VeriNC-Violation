#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 <sde_name>"
    exit 1
fi

function replace_string_in_file() {
    local file=$1
    local placeholder=$2
    local replacement=$3

    sed -i "s|$placeholder|$replacement|g" "$file"
}

# Replace placeholder SDE name in the clab file with the provided SDE name.

SDE_NAME=$1
PLACEHOLDER_SDE_NAME="tofino:20251025"
CLAB_FILE="topo.clab.yml"

replace_string_in_file "$CLAB_FILE" "$PLACEHOLDER_SDE_NAME" "$SDE_NAME"

# Replace hardcoded project directories with the current working directory.
WORK_DIR=$(pwd)
PLACEHOLDER_DIR="~/myrepo/verinc-switchml"

replace_string_in_file "$CLAB_FILE" "$PLACEHOLDER_DIR" "$WORK_DIR"

# Compile P4 code.
docker run -it --rm -v $WORK_DIR:/root/abc/switchml $SDE_NAME bash -ic \
    "bf-p4c --verbose 3 -g -a tna -b tofino --program-name SwitchML \
        -o /root/abc/switchml/dev_root/p4-build /root/abc/switchml/dev_root/p4/switchml.p4"

# Compile client library.
docker run -it --rm -v $WORK_DIR:/home/abc/switchml switchml-client:latest \
    bash -ic '\
        git config --global --add safe.directory /home/abc/switchml && \
        DIR=/home/switchml/dev_root/third_party && \
        make -C /home/abc/switchml/dev_root/client_lib DEBUG=1 DPDK=1 \
            DPDK_HOME=$DIR/dpdk/build DPDK_SDK=$DIR/dpdk GRPC_HOME=$DIR/grpc/build VCL_HOME=$DIR/vcl\
    '

# Compile hello_world example.
docker run -it --rm -v $WORK_DIR:/home/abc/switchml switchml-client:latest \
    bash -ic '\
        git config --global --add safe.directory /home/abc/switchml && \
        DIR=/home/switchml/dev_root/third_party && \
        cd /home/abc/switchml/dev_root && \
        rm -f build/bin/hello_world && \
        make -C examples DPDK=1 DEBUG=1 DPDK_HOME=$DIR/dpdk/build \
            DPDK_SDK=$DIR/dpdk GRPC_HOME=$DIR/grpc/build VCL_HOME=$DIR/vcl\
    '

# Compile controller.
docker run -it --rm -v $WORK_DIR:/home/abc/switchml switchml-tofino:latest \
    bash -ic 'make -C /home/abc/switchml/dev_root/controller GRPC_HOME=/usr'

echo
echo "Project setup completed successfully."
