#!/bin/bash
set -e

compile_method() {
    local method="$1"
    echo "[COMPILE][DOCKER] first compilation for ${method}"

    bash scripts/remote/setmethod.sh ${method}

    echo "[COMPILE][DOCKER] building switchos for ${method}"
    bash scripts/local/makeswitchos.sh
}

source /root/.bashrc
compile_method nocache
compile_method netcache

echo "[COMPILE][DOCKER] all methods compiled."