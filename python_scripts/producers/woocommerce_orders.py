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

sys.path.append(os.path.join('/home/etl_montredo/data-pipeline-python-kafka'))

import global_configuration
from python_scripts.database.woocommerce_tables import create_tables, session



def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


def produce_data(list_all_orders):
    for data in list_all_orders:
        # Trigger any available delivery report callbacks from previous produce() calls
        p.poll(0)
        # Asynchronously produce a message, the delivery report callback
        # will be triggered from poll() above, or flush() below, when the message has
        # been successfully delivered or failed permanently.
        p.produce('woocommerce_orders', data.encode('utf-8'), callback=delivery_report)
        # Wait for any outstanding messages to be delivered and delivery report
        # callbacks to be triggered.
    p.flush()


def get_last_updated_at():
    query = """SELECT MAX(date_created) as date_created, MAX(date_modified) as date_modified
               FROM woocommerce_en_de.orders;"""
    query_result = session.execute(query).fetchall()
    date_created = '2019-01-01' if query_result[0][0] == None else query_result[0][0]
    date_updated = '2019-01-01' if query_result[0][0] == None else query_result[0][1]
    return date_created, date_updated


def get_woocommerce_orders():
    key = global_configuration.Woocommerce.consumer_key
    secret = global_configuration.Woocommerce.consumer_secret
    url = global_configuration.Woocommerce.url
    wcapi = API(
        url=url,
        consumer_key=key,
        consumer_secret=secret,
        timeout=10
    )
    date_created, date_updated = get_last_updated_at()
    dict_new_orders = {}
    dict_update_orders = {}
    pages = 1
    for x in range(1, pages+1):
        delete-->r_new = wcapi.get("orders?after=2019-01-01T13:57:31.2311892-04:00").json()
        r_new = wcapi.get("orders?per_page=100&page={0}&after={1}".format(x, date_created)).json()
        #r_update = wcapi.get("orders?page={0}&after_update={1}".format(x, date_updated)).json()
        for new_order in r_new:
            dict_new_orders[new_order['id']] = {'created_at': new_order['created_at'],
                                                'updated_at': new_order['updated_at']
                                                }
        #for update_order in r_update:
        #    dict_update_orders[update_order['id']] = {'created_at': update_order['created_at'],
        #                                        'updated_at': update_order['updated_at']
        #                                        }
    return dict_new_orders# + dict_update_orders


if __name__=='__main__':
    create_tables()
    p = Producer({'bootstrap.servers': 'localhost:9092,localhost:9093'})
    sleep_time = 3
    try:
        while True:
            print('Sleeping for {0} seconds...'.format(sleep_time))
            time.sleep(sleep_time)
            list_all_orders = get_woocommerce_orders()
            produce_data(list_all_orders)
    except KeyboardInterrupt:
        pass

## Things to improve ##
# Make Woocommerce send request to Python script (Webhook on order create and update)