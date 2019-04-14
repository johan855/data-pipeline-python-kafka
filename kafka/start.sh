# Initiallize Zookeeper
nohup zookeeper-server-start.sh kafka_2.12-2.2.0/config/zookeeper.properties &
sleep 5
# Start 2 Kafka brokers (General setup for 3 partitions, 2 brokers and rep. factor of 2 per topic)
nohup kafka-server-start.sh kafka_2.12-2.2.0/config/server.0.properties &
sleep 5
nohup kafka-server-start.sh kafka_2.12-2.2.0/config/server.1.properties &


# Create first topic (3 partitions and 2 as rep. factor)
kafka-topics.sh --zookeeper localhost:2181 --topic first_topic --create --partitions 3 --replication-factor 2
# Create producer
python ./create_producer.py

# Create consumer
python ./create_consumer.py