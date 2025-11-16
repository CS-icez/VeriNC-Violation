FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Etc/UTC \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# 1. 基础工具和依赖
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
    gdb \
    iproute2 \
    && update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-7 70 \
    && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-7 70 \
    && rm -rf /var/lib/apt/lists/*

# 3. 配置 JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# 5. 准备项目目录（宿主机会挂载 /opt/farreach）
RUN mkdir -p /opt/farreach
WORKDIR /opt/farreach

# 6. Python 依赖（对应 README: pip install -r requirements.txt）
#   注意：Docker build 时必须能看到 requirements.txt（例如 docker build 时把仓库 COPY 进来）
COPY requirements.txt /opt/farreach/requirements.txt
RUN pip install --no-cache-dir -r /opt/farreach/requirements.txt || true

# 7. 编译 Boost 1.81.0（对应 README）
RUN mkdir -p /opt/deps && cd /opt/deps \
    && wget -O boost_1_81_0.tar.gz https://github.com/boostorg/boost/releases/download/boost-1.81.0/boost-1.81.0.tar.gz \
    && tar -xzvf boost_1_81_0.tar.gz \
    && cd boost-1.81.0 \
    && ./bootstrap.sh --with-libraries=system,thread --prefix=/opt/deps/boost_1_81_0/install \
    && ./b2 -j"$(nproc)" install

ENV BOOST_ROOT=/opt/deps/boost_1_81_0/install

# 8. RocksDB 静态库编译（对应 README 1.3）
#   假设仓库的 rocksdb-6.22.1 已经在构建上下文中
COPY rocksdb-6.22.1 /opt/farreach/rocksdb-6.22.1
WORKDIR /opt/farreach/rocksdb-6.22.1

RUN PORTABLE=1 make static_lib -j"$(nproc)" \
    && rm -rf .git

# 9. 预创建数据库目录（/tmp/farreach /tmp/nocache /tmp/netcache）
RUN mkdir -p /tmp/farreach /tmp/nocache /tmp/netcache

# 10. 默认工作目录回到项目根
WORKDIR /opt/farreach

# 设置 root 密码
RUN echo 'root:root' | chpasswd

# 修改 SSH 配置以允许 root 通过密码登录
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# 11. 暴露 ssh 端口，方便调试（可选）
EXPOSE 22

CMD ["/bin/bash"]