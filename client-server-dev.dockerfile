FROM farreach-client-server:base

WORKDIR /opt/farreach
COPY . /opt/farreach

RUN pip install --no-cache-dir -r requirements.txt || true

WORKDIR /opt/farreach
RUN bash docker_firstcompile.sh

CMD ["/bin/bash"]