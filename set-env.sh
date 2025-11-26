function build_docker() {
    docker build -f client-server.dockerfile -t farreach-client-server:latest .
    docker build -f tofino.dockerfile -t farreach-tofino:latest .
}

function update_config() {
    bash scripts/local/update_config_files.sh
}
