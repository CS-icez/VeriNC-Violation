function compile_p4() {
    docker run -it --rm -v ~/myrepo/verinc-switchml:/root/bty/switchml sde:9.7.0 bash -i -c \
        "bf-p4c --verbose 3 -g -a tna -b tofino --program-name SwitchML \
            -o /root/bty/switchml/dev_root/p4-build /root/bty/switchml/dev_root/p4/switchml.p4"
}

function make_client_lib() {
    docker run -it --rm -v ~/myrepo/verinc-switchml:/home/bty/switchml switchml-client:latest \
        bash -i -c '\
            git config --global --add safe.directory /home/bty/switchml && \
            DIR=/home/switchml/dev_root/third_party && \
            make -C /home/bty/switchml/dev_root/client_lib DEBUG=1 DPDK=1 \
                DPDK_HOME=$DIR/dpdk/build DPDK_SDK=$DIR/dpdk GRPC_HOME=$DIR/grpc/build VCL_HOME=$DIR/vcl\
        '
}

function make_hello_world() {
    docker run -it --rm -v ~/myrepo/verinc-switchml:/home/bty/switchml switchml-client:latest \
        bash -i -c '\
            git config --global --add safe.directory /home/bty/switchml && \
            DIR=/home/switchml/dev_root/third_party && \
            cd /home/bty/switchml/dev_root && \
            rm build/bin/hello_world && \
            make -C examples DPDK=1 DEBUG=1 DPDK_HOME=$DIR/dpdk/build \
                DPDK_SDK=$DIR/dpdk GRPC_HOME=$DIR/grpc/build VCL_HOME=$DIR/vcl\
        '
}