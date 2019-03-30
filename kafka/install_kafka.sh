#!/bin/bash

# Install confluent-kafka in python
pip install confluent-kafka

# Download and unzip Kafka
sudo apt install openjdk-8-jdk
cd ~
wget "http://www-eu.apache.org/dist/kafka/1.0.1/kafka_2.12-1.0.1.tgz"
tar -xvf kafka_2.12-1.0.1.tgz

# Add Kafka to PATH
echo "export PATH=~/.local/bin:$PATH" >> .bashrc
echo "export PATH=/home/etl_montredo/kafka_2.12-2.1.1/bin:$PATH" >> .bashrc

# Create data folders and modify property config (log folders and ports)
mkdir ~/kafka_2.12-2.1.1/data
mkdir ~/kafka_2.12-2.1.1/data/zookeeper
mkdir ~/kafka_2.12-2.1.1/data/kafka0
mkdir ~/kafka_2.12-2.1.1/data/kafka1


# Modify log folders
sed -i -e '/dataDir/ s/\/tmp\/zookeeper/~\/kafka_2.12-2.1.1\/data\/zookeeper/' \
    kafka_2.12-2.1.1/config/zookeeper.properties
sed -i -e '/dataDir/ s/\/tmp\/kafka-logs/~\/kafka_2.12-2.1.1\/data\/kafka0/' \
    kafka_2.12-2.1.1/config/server.0.properties
sed -i -e '/dataDir/ s/\/tmp\/kafka-logs/~\/kafka_2.12-2.1.1\/data\/kafka1/' \
    kafka_2.12-2.1.1/config/server.1.properties


# Create Kafka broker config files (2 brokers)
cp kafka_2.12-2.1.1/config/server.properties kafka_2.12-2.1.1/config/server.0.properties
cp kafka_2.12-2.1.1/config/server.properties kafka_2.12-2.1.1/config/server.1.properties

# Modify broker.id in config files
sed -i -e '/broker.id/ s/0/1/' kafka_2.12-2.1.1/config/server.1.properties

# Modify listeners in config files
sed -i -e '/listeners=PLAINTEXT:\/\/:9092/ s/^#//' kafka_2.12-2.1.1/config/server.0.properties
sed -i -e '/listeners=PLAINTEXT:\/\/:9092/ s/^#//' kafka_2.12-2.1.1/config/server.1.properties
sed -i -e '/listeners/ s/PLAINTEXT:\/\/:9092/PLAINTEXT:\/\/:9093/' kafka_2.12-2.1.1/config/server.1.properties


# Initiallize Zookeeper
nohup zookeeper-server-start.sh kafka_2.12-2.1.1/config/zookeeper.properties &
sleep 5
# Start 2 Kafka brokers (General setup for 3 partitions, 2 brokers and rep. factor of 2 per topic)
nohup kafka-server-start.sh kafka_2.12-2.1.1/config/server.0.properties &
sleep 5
nohup kafka-server-start.sh kafka_2.12-2.1.1/config/server.1.properties &


# Create first topic (3 partitions and 2 as rep. factor)
kafka-topics.sh --zookeeper localhost:2181 --topic first_topic --create --partitions 3 --replication-factor 2
# Create consumer (after producer in python)
