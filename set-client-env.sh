function run() {
    local hostname=$(hostname)
    if [[ "$hostname" == "client0" ]]; then
        $PROJ_DIR/client/app 0 2 1 1 # &> $PROJ_DIR/log/client0.log
    elif [[ "$hostname" == "client1" ]]; then
        $PROJ_DIR/client/app 1 2 1 1 # &> $PROJ_DIR/log/client1.log
    else
        echo "Unknown hostname: $hostname"
    fi
}