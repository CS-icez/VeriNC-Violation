FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Etc/UTC \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Basic tools and dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    wget curl git ca-certificates \
    openssh-client openssh-server sshpass \
    screen sudo vim \
    python python-pip \
    openjdk-8-jdk \
    maven \
    libgflags-dev libsnappy-dev zlib1g-dev libbz2-dev \
    liblz4-dev libzstd-dev libjemalloc-dev \
    pkg-config \
    gcc-7 g++-7 \
    iproute2 net-tools \
    psmisc \
    bc \
    rsync \
    gdb \
    && update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-7 70 \
    && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-7 70 \
    && rm -rf /var/lib/apt/lists/*

# Configure JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# Prepare project directory
RUN mkdir -p /opt/farreach
WORKDIR /opt/farreach
COPY . .

# Python dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# Build Boost 1.81.0 from source
RUN mkdir -p /opt/deps && cd /opt/deps \
    && wget -O boost_1_81_0.tar.gz https://github.com/boostorg/boost/releases/download/boost-1.81.0/boost-1.81.0.tar.gz \
    && tar -xzvf boost_1_81_0.tar.gz \
    && cd boost-1.81.0 \
    && ./bootstrap.sh --with-libraries=system,thread --prefix=/opt/deps/boost_1_81_0/install \
    && ./b2 -j"$(nproc)" install
RUN ln -s /opt/deps/boost_1_81_0 /opt/farreach/boost_1_81_0
ENV BOOST_ROOT=/opt/deps/boost_1_81_0/install

# Build RocksDB static library from source
WORKDIR /opt/farreach/rocksdb-6.22.1

RUN PORTABLE=1 make static_lib -j"$(nproc)" \
    && rm -rf .git

# Pre-create database directories (/tmp/farreach /tmp/nocache /tmp/netcache)
RUN mkdir -p /tmp/farreach /tmp/nocache /tmp/netcache

# Reset default working directory to project root
WORKDIR /opt/farreach

# Set root password
RUN echo 'root:root' | chpasswd

# Modify SSH config to allow root login with password
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Expose SSH port
EXPOSE 22

# Compile project
RUN bash docker_firstcompile_client_server.sh

CMD ["/bin/bash"]
