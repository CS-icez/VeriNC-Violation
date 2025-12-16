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
PLACEHOLDER_DIR="~/myrepo/verinc-fisslock"
ENV_FILE="experiments/set-env.sh"

replace_string_in_file "$CLAB_FILE" "$PLACEHOLDER_DIR" "$WORK_DIR"
replace_string_in_file "$ENV_FILE" "$PLACEHOLDER_DIR" "$WORK_DIR"

# Compile P4 code.
source $ENV_FILE

docker run -it --rm -v $LOCAL_PROJ_PATH:$SWITCH_PROJ_PATH $SDE_NAME bash -ic \
    "bf-p4c --verbose 3 -g -a tna -b tofino --program-name fisslock_decider \
        -o $SWITCH_PROJ_PATH/fisslock-p4-build $SWITCH_PROJ_PATH/switch/p4/switch.p4"

# Compile switch control plane.
docker run -it --rm -v $LOCAL_PROJ_PATH:$SWITCH_PROJ_PATH $SDE_NAME bash -ic " \
    mkdir -p /tmp  && \
    cd /root/onl-bf-bsp/bf-platforms && \
    cp -rv $SWITCH_PROJ_PATH/switch/control/* fisslock && \
    autoreconf && \
    export PKG_CONFIG_PATH=\$SDE_INSTALL/lib/pkgconfig && \
    ./configure --prefix=\$SDE_INSTALL --enable-grpc --enable-thrift --host=x86_64-linux-gnu && \
    cd fisslock && \
    make && make install && \
    cp \$SDE_INSTALL/bin/fisslock_decider $SWITCH_PROJ_PATH/build \
"

# Compile server code.
docker run -it --rm -v $LOCAL_PROJ_PATH:$MASTER_FISSLOCK_PATH dpdk:v21.11.4 bash -ic \
    "make -C $MASTER_FISSLOCK_PATH"

echo
echo "Project setup completed successfully."
