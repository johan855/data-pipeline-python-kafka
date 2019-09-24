Python-Kafka data pipeline for Woocommerce
==========================

This repo contains the necessary scripts to install and deploy Kafka as the main ETL
service for a Woocommerce shop.

Kafka details:
--------------
1) 2 Brokers
2) 1 topic per WC endpoint with 3 partitions and rep-factor of 2
3) Python based producers and consumers
4) Apache flink as a stream data processing platform

Workflow:
---------
A Python producer downloads data from the Woocommerce API loading orders to one raw data layer topic per endpoint.
A KSQL process creates aggregate layers of data from the raw data layer topics.
A Python consumer loads data from the different layers into the database and tools.

Issues:
-------
The Woocommerce API does not contain "updated_at" information on its endpoints, which makes it impossible to have an incremental stream of data. A workaround in place is to receive on a different Kafka Topic a set of webhook calls which are triggered in the event of a data update. this process is more close to an event streaming pipeline than a batch but may become complicated to implement each webhook independently for each update.
