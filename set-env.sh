function build_docker() {
    docker build -f client-server.dockerfile -t netcache-client-server:latest .
    docker build -f tofino.dockerfile -t netcache-tofino:latest .
}

function sync_docker() {
    # `docker run ---mount` shadows the whole directory, but `COPY` shadows files one by one.
    echo -e 'FROM netcache-client-server:latest\nCOPY . .' | docker build -t netcache-client-server:latest -f - .
    echo -e 'FROM netcache-tofino:latest\nCOPY . .' | docker build -t netcache-tofino:latest -f - .
    docker image prune -f
}

function update_config() {
    bash scripts/local/update_config_files.sh
}
