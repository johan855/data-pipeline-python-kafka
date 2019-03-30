Python-Kafka data pipeline for Woocommerce
==========================

This repo contains the necessary scripts to install and deploy Kafka as the main ETL
service for a Woocommerce shop.

Kafka details:
--------------
1) 2 Brokers
2) 1 topic per WC endpoint with 3 partitions and replication-factor of 2
3) Python based producers and consumers