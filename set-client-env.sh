function run() {
    local hostname=$(hostname)
    if [[ "$hostname" == "client0" ]]; then
        export DPDK_EAL_ARGS="--vdev=net_af_packet0,iface=veth --no-huge -l 1-2"
        stdbuf -oL $PROJ_DIR/client/app 0 2 1 1 &> $PROJ_DIR/log/client0.log
    elif [[ "$hostname" == "client1" ]]; then
        export DPDK_EAL_ARGS="--vdev=net_af_packet0,iface=veth --no-huge -l 3-4"
        stdbuf -oL $PROJ_DIR/client/app 1 2 1 1 &> $PROJ_DIR/log/client1.log
    else
        echo "Unknown hostname: $hostname"
    fi
}