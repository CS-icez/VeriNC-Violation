FROM tofino:20251025

RUN mkdir -p /tmp /run && \
    apt-get update && \
    apt-get install -y \
    sshpass && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt/farreach
COPY . .
RUN bash docker_firstcompile_tofino.sh

CMD ["/bin/bash"]
