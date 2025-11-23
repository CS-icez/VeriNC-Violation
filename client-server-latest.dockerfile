FROM farreach-client-server:dev
COPY . /opt/farreach
RUN cd benchmark/ycsb && mvn -pl site.ycsb:core -am package -DskipTests