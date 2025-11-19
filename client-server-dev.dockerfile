FROM farreach-client-server:base

WORKDIR /opt/farreach
COPY . /opt/farreach
RUN ln -s /opt/deps/boost_1_81_0 /opt/farreach/boost_1_81_0

# RUN pip install --no-cache-dir -r requirements.txt || true

WORKDIR /opt/farreach
RUN bash docker_firstcompile.sh

CMD ["/bin/bash"]