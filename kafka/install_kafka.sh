#!/bin/bash

# Install confluent-kafka in python
pip install confluent-kafka

# Download and unzip Kafka
sudo apt install openjdk-8-jdk maven
cd ~
wget "https://www-us.apache.org/dist/kafka/2.2.0/kafka_2.12-2.2.0.tgz"
tar -xvf kafka_2.12-2.2.0.tgz

# Add Kafka to PATH
echo "export PATH=~/.local/bin:$PATH" >> .bashrc
echo "export PATH=/home/$USER/kafka_2.12-2.2.0/bin:$PATH" >> .bashrc

# Create data folders and modify property config (log folders and ports)
mkdir ~/kafka_2.12-2.2.0/data
mkdir ~/kafka_2.12-2.2.0/data/zookeeper
mkdir ~/kafka_2.12-2.2.0/data/kafka0
mkdir ~/kafka_2.12-2.2.0/data/kafka1


# Create Kafka broker config files (2 brokers)
cp kafka_2.12-2.2.0/config/server.properties kafka_2.12-2.2.0/config/server.0.properties
cp kafka_2.12-2.2.0/config/server.properties kafka_2.12-2.2.0/config/server.1.properties

# Modify log folders
sed -i -e '/dataDir/ s/\/tmp\/zookeeper/\/home\/etl_montredo\/kafka_2.12-2.2.0\/data\/zookeeper/' \
    kafka_2.12-2.2.0/config/zookeeper.properties
sed -i -e '/log.dirs/ s/\/tmp\/kafka-logs/\/home\/etl_montredo\/kafka_2.12-2.2.0\/data\/kafka0/' \
    kafka_2.12-2.2.0/config/server.0.properties
sed -i -e '/log.dirs/ s/\/tmp\/kafka-logs/\/home\/etl_montredo\/kafka_2.12-2.2.0\/data\/kafka1/' \
    kafka_2.12-2.2.0/config/server.1.properties

# Modify broker.id in config files
sed -i -e '/broker.id/ s/0/1/' kafka_2.12-2.2.0/config/server.1.properties

# Modify listeners in config files
sed -i -e '/listeners=PLAINTEXT:\/\/:9092/ s/^#//' kafka_2.12-2.2.0/config/server.0.properties
sed -i -e '/listeners=PLAINTEXT:\/\/:9092/ s/^#//' kafka_2.12-2.2.0/config/server.1.properties
sed -i -e '/listeners/ s/PLAINTEXT:\/\/:9092/PLAINTEXT:\/\/:9093/' kafka_2.12-2.2.0/config/server.1.properties


# Install KSQL (wget)
wget "https://github.com/confluentinc/ksql/releases/download/v0.4/ksql-0.4.tgz"
tar -xvf ksql-0.4.tgz

# Add KSQL to PATH
echo "export PATH=/home/$USER/ksql/bin:$PATH" >> .bashrc

## Things to improve ##
#  9 - Adapt to load always newest version of Kafka (implement version in variable instead of hardcoding it)
# 28 - Make sed commands set $HOME as variable instead of hardcoding it