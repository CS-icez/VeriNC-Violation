function build_cs_base() {
    docker build -f client-server-base.dockerfile -t farreach-client-server:base .
}

function build_cs_dev() {
    docker build -f client-server-dev.dockerfile -t farreach-client-server:dev .
}
