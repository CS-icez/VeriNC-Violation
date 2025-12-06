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
PLACEHOLDER_DIR="~/myrepo/verinc-netcache"

replace_string_in_file "$CLAB_FILE" "$PLACEHOLDER_DIR" "$WORK_DIR"

# Compile P4 code.
docker run -it --rm -v $WORK_DIR:/opt/netcache netcache-tofino:latest bash -ic \
    'export PROJ_DIR=/opt/netcache && source $PROJ_DIR/set-tofino-env.sh && compile_p4'

echo
echo "Project setup completed successfully."
