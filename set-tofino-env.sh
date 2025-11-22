function compile_p4() {
    cd /
    bf-p4c --verbose 3 -g -a tna -b tofino --program-name netbufferv4 \
        -o $PROJ_DIR/farreach-p4-build $PROJ_DIR/farreach/tofino/netbufferv4.p4
    bf-p4c --verbose 3 -g -a tna -b tofino --program-name nocache_16 \
        -o $PROJ_DIR/nocache-p4-build $PROJ_DIR/nocache/tofino/nocache_16.p4
    cd -
}
