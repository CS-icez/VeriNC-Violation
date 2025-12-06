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
PLACEHOLDER_DIR="~/myrepo/verinc-atp"

replace_string_in_file "$CLAB_FILE" "$PLACEHOLDER_DIR" "$WORK_DIR"

# Compile P4 code.
TOFINO_PROJ_DIR="/root/$abc/atp"
echo "Client/Server project directory set to: $CS_PROJ_DIR"

docker run -it --rm -v $WORK_DIR:$TOFINO_PROJ_DIR $SDE_NAME bash -ic " \
    bf-p4c --verbose 3 -g -a tna -b tofino --program-name p4ml16 \
        -o $TOFINO_PROJ_DIR/p4-16-build $TOFINO_PROJ_DIR/atp-p4-16/main.p4 \
"

# Compile client and server.
CS_PROJ_DIR="/root/atp"
docker run -it --rm -v $WORK_DIR:$CS_PROJ_DIR dpdk:v21.11.4 \
    bash -c "make -C $CS_PROJ_DIR/client && make -C $CS_PROJ_DIR/server"

echo
echo "Project setup completed successfully."
