function compile_p4() {
    cd /
    bf-p4c --verbose 3 -g -a tna -b tofino --program-name netcache \
        -o $PROJ_DIR/netcache-p4-build $PROJ_DIR/netcache/tofino/netcache.p4
    bf-p4c --verbose 3 -g -a tna -b tofino --program-name nocache_16 \
        -o $PROJ_DIR/nocache-p4-build $PROJ_DIR/nocache/tofino/nocache_16.p4
    cd -
}
