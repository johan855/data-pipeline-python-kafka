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
        print('Message delivery failed: {0}'.format(err))
    else:
        print('Message delivered to {0} [{1}]'.format(msg.topic(), msg.partition()))


def produce_data(dict_new_orders):
    for data in dict_new_orders:
        # Trigger any available delivery report callbacks from previous produce() calls
        p.poll(0)
        # Asynchronously produce a message, the delivery report callback
        # will be triggered from poll() above, or flush() below, when the message has
        # been successfully delivered or failed permanently.
        p.produce('woocommerce_orders', str(dict_new_orders[data]).encode('utf-8'), callback=delivery_report)
        # Wait for any outstanding messages to be delivered and delivery report
        # callbacks to be triggered.
    p.flush()


def get_last_updated_at():
    query_dates = """SELECT MAX(date_created) as date_created, MAX(date_modified) as date_modified
                     FROM woocommerce_en_de.orders;"""
    query_dates_result = session.execute(query_dates).fetchall()
    date_created = '2019-01-01T00:00:00' if query_dates_result[0][0] == None else query_dates_result[0][0]
    date_updated = '2019-01-01T00:00:00' if query_dates_result[0][0] == None else query_dates_result[0][1]
    return date_created, date_updated


def get_orders_dict():
    orders_dict = {}
    query_orders_list = """SELECT * FROM woocommerce_en_de.orders;"""
    query_orders_list_result = session.execute(query_orders_list).fetchall()
    orders_list = query_orders_list_result[0]
    for x in orders_list:
        orders_dict[x[0]]=x # Index has to be order_id
    return orders_dict

def get_woocommerce_orders(date_created, date_updated, orders_dict):
    key = global_configuration.Woocommerce.consumer_key
    secret = global_configuration.Woocommerce.consumer_secret
    url = global_configuration.Woocommerce.url
    wcapi = API(
        url=url,
        consumer_key=key,
        consumer_secret=secret,
        timeout=10
    )
    dict_new_orders = {}
    dict_update_orders = {}
    pages = 1
    for x in range(1, pages+1):
        r_new = wcapi.get("orders?per_page=100&page={0}&after={1}".format(x, date_created)).json()
        r_update = wcapi.get("orders?per_page=100&page={0}&before={1}".format(x, date_created)).json()
        for new_order in r_new:
            date_created = new_order['date_created_gmt'] if new_order['date_created_gmt'] >= date_created else date_created
            dict_new_orders[new_order['id']] = {'created_at': new_order['date_created'],
                                                'updated_at': new_order['date_updated']
                                                }
        for update_order in r_update:
            if update_order['date_modified_gmt'] < orders_dict[update_order['id']]['dwh_updated_at']:
                dict_update_orders[update_order['id']] = {'created_at': update_order['date_created_gmt'],
                                                    'updated_at': update_order['date_modified_gmt']
                                                    }
    return dict_new_orders + dict_update_orders, date_created


if __name__=='__main__':
    create_tables()
    p = Producer({'bootstrap.servers': 'localhost:9092,localhost:9093'})
    date_created, date_updated = get_last_updated_at()
    sleep_time = 3
    loop_value = -1
    try:
        while True:
            orders_dict = []
            loop_value += 1
            if loop_value>=5:
                # Load orders only every 5th iteration
                loop_value = -1
                orders_dict = get_orders_dict()
            print('Sleeping for {0} seconds...'.format(sleep_time))
            time.sleep(sleep_time)
            dict_new_orders, date_created = get_woocommerce_orders(date_created, date_updated, orders_dict)
            produce_data(dict_new_orders)
    except KeyboardInterrupt:
        pass

## Things to improve ##
# Make Woocommerce send request to Python script (Webhook on order create and update)