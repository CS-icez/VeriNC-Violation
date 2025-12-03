function run() {
    export ATP_SERVER_LOG=1
    export DPDK_EAL_ARGS="--vdev=net_af_packet0,iface=veth --no-huge -l 0"
    stdbuf -oL $PROJ_DIR/server/app 1 &> $PROJ_DIR/log/server.log
}
