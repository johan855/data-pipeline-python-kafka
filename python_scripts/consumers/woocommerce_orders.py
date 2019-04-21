import os
import sys
import json
from confluent_kafka import Consumer, KafkaError

sys.path.append(os.path.join('/home/etl_montredo/data-pipeline-python-kafka'))

from python_scripts.database.woocommerce_tables import create_tables, session, Orders


def load_to_db(msg):
    data = json.loads(msg.value().decode('utf8').replace("'",'"'))
    orders_data = Orders(
                         order_id=data['order_id'],
                         date_created=data['date_created'],
                         date_modified=data['date_modified']
                         )
    session.merge(orders_data)
    session.commit()
    session.close()
    print('Loaded data: {}'.format(msg.value().decode('utf-8')))


if __name__=='__main__':
    create_tables()
    c = Consumer({
        'bootstrap.servers': 'localhost:9092,localhost:9093',
        'group.id': 'woocommerce',
        'auto.offset.reset': 'earliest'
    })
    c.subscribe(['woocommerce_orders'])
    while True:
        msg = c.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue
        load_to_db(msg)
    c.close()