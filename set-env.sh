PROJ_DIR=~/myrepo/verinc-farreach

function build_cs_base() {
    cd $PROJ_DIR
    docker build -f client-server-base.dockerfile -t farreach-client-server:base .
    cd -
}

function build_cs_dev() {
    cd $PROJ_DIR
    docker build -f client-server-dev.dockerfile -t farreach-client-server:dev .
    cd -
}

function update_config() {
    cd $PROJ_DIR
    bash scripts/local/update_config_files.sh
    cd -
}