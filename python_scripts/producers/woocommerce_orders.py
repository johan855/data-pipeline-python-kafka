#To Do:
#use github: https://github.com/confluentinc/confluent-kafka-python
#https://www.confluent.io/blog/introduction-to-apache-kafka-for-python-programmers/
#Learn about google proto buffs
import os
import sys
import time
import logging
from woocommerce import API
from datetime import timedelta
from collections import defaultdict
from datetime import datetime as dt
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


def produce_data(orders):
    for data in orders:
        # Trigger any available delivery report callbacks from previous produce() calls
        p.poll(0)
        # Asynchronously produce a message, the delivery report callback
        # will be triggered from poll() above, or flush() below, when the message has
        # been successfully delivered or failed permanently.
        p.produce('woocommerce_orders', str(orders[data]).encode('utf-8'), callback=delivery_report)
        # Wait for any outstanding messages to be delivered and delivery report
        # callbacks to be triggered.
    p.flush()


def get_last_updated_at():
    query_dates = """SELECT MAX(date_created) as date_created, MAX(date_modified) as date_modified
                     FROM woocommerce_en_de.orders;"""
    query_dates_result = session.execute(query_dates).fetchall()
    date_created = dt.strptime('2019-01-01T00:00:00', "%Y-%m-%dT%H:%M:%S") if query_dates_result[0][0] == None else \
        query_dates_result[0][0]
    date_updated = dt.strptime('2019-01-01T00:00:00', "%Y-%m-%dT%H:%M:%S") if query_dates_result[0][0] == None else \
        query_dates_result[0][1]
    return date_created, date_updated


def get_orders_dict():
    orders_dict = {}
    query_orders_list = """SELECT * FROM woocommerce_en_de.orders;"""
    query_orders_list_result = session.execute(query_orders_list).fetchall()
    if len(query_orders_list_result) > 0:
        query_orders_list_result
        for x in query_orders_list_result:
            orders_dict[x[1]]= {"id": x[1],
                                "date_created": x[2],
                                "date_modified": x[3],
                                "dwh_created_at": x[4],
                                "dwh_updated_at": x[5]
                                }
    return orders_dict

def get_woocommerce_orders(date_created, date_updated, orders_dict):
    """Date updated still unused, need to include when updated_at is available in WC API"""
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
    date_created_string = date_created.strftime('%Y-%m-%dT%H:%M:%S')
    pages = 1
    for x in range(1, pages+1):
        r_new = wcapi.get("orders?per_page=100&page={0}&after={1}".format(x, date_created_string)).json()
        r_update = wcapi.get("orders?per_page=100&page={0}&before={1}".format(x, date_created_string)).json()
        for new_order in r_new:
            new_order_date_created = dt.strptime(new_order['date_created_gmt'], "%Y-%m-%dT%H:%M:%S")
            new_order_date_modified = dt.strptime(new_order['date_modified_gmt'], "%Y-%m-%dT%H:%M:%S")
            new_order_id = str(new_order['id'])
            new_date_created = dt.strptime(new_order['date_created_gmt'], "%Y-%m-%dT%H:%M:%S")
            date_created = new_date_created if new_order_date_created >= date_created else date_created
            dict_new_orders[new_order_id] = {"order_id": new_order_id,
                                             "date_created": new_order['date_created_gmt'],
                                             "date_modified": new_order['date_modified_gmt']
                                             }
        if len(orders_dict) > 0:
            for update_order in r_update:
                update_order_id = str(update_order['id'])
                if update_order_id in orders_dict:
                    update_order_date_created = dt.strptime(update_order['date_created_gmt'], "%Y-%m-%dT%H:%M:%S")
                    update_order_date_modified = dt.strptime(update_order['date_modified_gmt'], "%Y-%m-%dT%H:%M:%S")
                    if orders_dict[update_order_id]['date_modified'] != None:
                        orders_dict_date_modified = orders_dict[update_order_id]['date_modified']
                    else:
                        # Assign -1 day so next first condition always True
                        orders_dict_date_modified = update_order_date_modified - timedelta(days=1)
                    if update_order_date_modified > orders_dict_date_modified and update_order not in r_new:
                        # Check if > condition is enough (it was => before)
                        dict_update_orders[update_order_id] = {"order_id": update_order_id,
                                                               "date_created": update_order['date_created_gmt'],
                                                               "date_modified": update_order['date_modified_gmt']
                                                               }
    orders = dict_new_orders.copy()
    orders.update(dict_update_orders)
    return orders, date_created


if __name__=='__main__':
    create_tables()
    p = Producer({'bootstrap.servers': 'localhost:9092,localhost:9093'})
    date_created, date_updated = get_last_updated_at()
    sleep_time = 3
    loop_value = 0
    try:
        while True:
            orders_dict = []
            loop_value += 1
            if loop_value>=5:
                # Load orders only every 5th iteration
                loop_value = -1
                orders_dict = get_orders_dict()
            #print('Sleeping for {0} seconds...'.format(sleep_time))
            time.sleep(sleep_time)
            orders, date_created = get_woocommerce_orders(date_created, date_updated, orders_dict)
            produce_data(orders)
    except KeyboardInterrupt:
        pass

## Things to improve ##
# Make Woocommerce send request to Python script (Webhook on order create and update)
# Use pandas to zip dict keys
# Fix offset management (What happens if the process breaks? will all messages have to be reloaded from the start?)
# Check why producer only kicks in on create order (doesnt produce only updates until an orders is created)