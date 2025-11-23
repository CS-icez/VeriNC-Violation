#!/bin/bash
set -e

compile_method() {
    local method="$1"
    echo "[COMPILE][DOCKER] first compilation for ${method}"

    bash scripts/remote/setmethod.sh ${method}

    echo "[COMPILE][DOCKER] building client for ${method}"
    bash scripts/local/makeclient.sh

    echo "[COMPILE][DOCKER] building server for ${method}"
    bash scripts/local/makeserver.sh

    echo "[COMPILE][DOCKER] building switchos for ${method}"
    bash scripts/local/makeswitchos.sh
}

source /root/.bashrc
compile_method nocache
compile_method farreach

echo "[COMPILE][DOCKER] all methods compiled."