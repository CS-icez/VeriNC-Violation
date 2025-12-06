FROM patrickkutch/dpdk:v21.11.4

RUN apt update && \
    apt install -y libboost-program-options-dev libgoogle-glog-dev && \
    apt install -y libibverbs-dev libhugetlbfs-dev libssl-dev && \
    apt install -y openssh-server sshpass && \
    apt install -y iptables python3-pip && \
    rm -rf /var/lib/apt/lists/* && \
    pip install paramiko && \
    mkdir -p /var/run/sshd

RUN echo 'root:root' | chpasswd

RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

EXPOSE 22

ENTRYPOINT []
