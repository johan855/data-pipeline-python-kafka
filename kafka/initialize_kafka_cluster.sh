#!/bin/bash

# 1) Source connectors
# Open ports to be used (3030 for Landoop UI)
# Start our kafka cluster
# Errors in distr. mode are on localhost:3030/logs/
docker-compose up kafka-cluster

###############
# A) FileStreamSourceConnector in standalone mode
# Look at the source/demo-1/worker.properties file and edit bootstrap
# Look at the source/demo-1/file-stream-demo.properties file
# Look at the demo-file.txt file

# We start a hosted tools, mapped on our code
# Linux / Mac
docker run --rm -it -v "$(pwd)":/tutorial --net=host landoop/fast-data-dev:cp3.3.0 bash

# we launch the kafka connector in standalone mode:
cd /tutorial/source/demo-1
# create the topic we write to with 3 partitions
kafka-topics --create --topic demo-1-standalone --partitions 3 --replication-factor 1 --zookeeper 127.0.0.1:2181
# Usage is connect-standalone worker.properties connector1.properties [connector2.properties connector3.properties]
connect-standalone worker.properties file-stream-demo-standalone.properties
# write some data to the demo-file.txt !
# shut down the terminal when you're done.
###############

###############
# B) FileStreamSourceConnector in distributed mode:
# create the topic we're going to write to
docker run --rm -it --net=host landoop/fast-data-dev:cp3.3.0 bash
kafka-topics --create --topic demo-2-distributed --partitions 3 --replication-factor 1 --zookeeper 127.0.0.1:2181
# you can now close the new shell

# head over to 127.0.0.1:3030 -> Connect UI
# Create a new connector -> File Source
# Paste the configuration at source/demo-2/file-stream-demo-distributed.properties

# Now that the configuration is launched, we need to create the file demo-file.txt
docker ps
docker exec -it <containerId> bash
touch demo-file.txt
echo "hi" >> demo-file.txt
echo "hello" >> demo-file.txt
echo "from the other side" >> demo-file.txt

# Read the topic data
docker run --rm -it --net=host landoop/fast-data-dev:cp3.3.0 bash
kafka-console-consumer --topic demo-2-distributed --from-beginning --bootstrap-server 127.0.0.1:9092
# observe we now have json as an output, even though the input was text!
###############

###############
# C) TwitterSourceConnector in distributed mode:
# create the topic we're going to write to
docker run --rm -it --net=host landoop/fast-data-dev:cp3.3.0 bash
kafka-topics --create --topic demo-3-twitter --partitions 3 --replication-factor 1 --zookeeper 127.0.0.1:2181
# Start a console consumer on that topic
kafka-console-consumer --topic demo-3-twitter --bootstrap-server 127.0.0.1:9092

# Follow the instructions at: https://github.com/Eneco/kafka-connect-twitter#creating-a-twitter-application
# To obtain the required keys, visit https://apps.twitter.com/ and Create a New App.
#Fill in an application name & description & web site and accept the developer aggreement.
#Click on Create my access token and populate a file twitter-source.properties with consumer key & secret
#and the access token & token secret using the example file to begin with.

# Setup instructions for the connector are at: https://github.com/Eneco/kafka-connect-twitter#setup
# fill in the required information at demo-3/source-twitter-distributed.properties
# Launch the connector and start seeing the data flowing in!
