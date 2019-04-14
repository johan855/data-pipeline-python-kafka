#To Do:
#use github: https://github.com/confluentinc/confluent-kafka-python
#https://www.confluent.io/blog/introduction-to-apache-kafka-for-python-programmers/
#Learn about google proto buffs

import os
import sys
import time
import logging
from woocommerce import API
from confluent_kafka import Producer
from confluent_kafka import admin.AdminClient as admin

sys.path.append(os.path.join('C:\\Users\\Johan\\PycharmProjects\\analytics-from-cloud\\kafka\\python_scripts'))

import global_configuration


def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


def produce_data(list_of_orders):
    for data in list_of_orders:
        # Trigger any available delivery report callbacks from previous produce() calls
        p.poll(0)
        # Asynchronously produce a message, the delivery report callback
        # will be triggered from poll() above, or flush() below, when the message has
        # been successfully delivered or failed permanently.
        p.produce('mytopic', data.encode('utf-8'), callback=delivery_report)
        # Wait for any outstanding messages to be delivered and delivery report
        # callbacks to be triggered.
    p.flush()


def get_orders():
    key = Woocommerce.consumer_key
    secret = Woocommerce.consumer_secret
    url = Woocommerce.url
    wcapi = API(
        url=url,
        consumer_key=key,
        consumer_secret=secret,
        timeout=10
    )
    response = ''
    list_of_orders = []
    pages = 1
    for x in range(1, pages+1):
        r = wcapi.get("orders?page={0}".format(x)).json()
        for order in r:
            list_of_orders.append(order)
    return list_of_orders


if __name__=='__main__':
    p = Producer({'bootstrap.servers': 'localhost:9092,localhost:9093'})
    sleep_time = 3
    try:
        while True:
            print('Sleeping for {0} seconds...'.format(sleep_time))
            time.sleep(sleep_time)
            list_of_orders = get_orders()
            produce_data(list_of_orders)
    except KeyboardInterrupt:
        pass
