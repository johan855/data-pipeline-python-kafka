#docker network create flink-net
#docker run --name flink-master --net flink-net -e ENABLE_INIT_DAEMON=false -d bde2020/flink-master:1.7.2-hadoop2.8
#docker run --name flink-worker --net flink-net -e ENABLE_INIT_DAEMON=false -e FLINK_MASTER_PORT_6123_TCP_ADDR=flink-master -d bde2020/flink-worker:1.7.2-hadoop2.8

docker-compose up -d
