# Kafka cat for list of messages (Docker consumer)
docker run --tty --interactive --rm \
          confluentinc/cp-kafkacat \
          kafkacat -b kafka:9092 \
          -C -t woocommerce_orders \
          -o beginning

