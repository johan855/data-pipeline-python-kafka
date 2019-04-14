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

sys.path.append(os.path.join('C:\\Users\\Johan\\PycharmProjects\\data-pipeline-python-kafka\\python_scripts'))

import global_configuration
from helpers import db_connection as db



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
        p.produce('woocommerce_orders', data.encode('utf-8'), callback=delivery_report)
        # Wait for any outstanding messages to be delivered and delivery report
        # callbacks to be triggered.
    p.flush()


def get_last_updated_at():
    con_yml_dict = {
        'db_user': global_configuration.DwhPsql.db_user,
        'db_passwd': global_configuration.DwhPsql.db_passwd,
        'db_name': global_configuration.DwhPsql.db_name,
        'db_host': global_configuration.DwhPsql.db_host
    }

    db_conn = db.DBconnection(config_path=con_yml_dict, schema='dwh_il')
    session = db_conn.get_session()
    query = """SELECT MAX(date_created) as date_created, MAX(date_modified) as date_modified
               FROM woocommerce_en_de;"""
    query_result = session.execute(query).fetchall()


def get_woocommerce_orders():
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
    list_new_orders = []
    list_update_orders = []
    pages = 1
    for x in range(1, pages+1):
        r_new = wcapi.get("orders?page={0}&date_created_gmt={1}".format(x)).json()
        r_update = wcapi.get("orders?page={0}&date_modified_gmt={1}".format(x)).json()
        for new_order in r_new:
            list_new_orders.append(new_order)
        for update_order in r_update:
            list_update_orders.append(update_order)
    return list_of_orders, list_update_orders


if __name__=='__main__':
    p = Producer({'bootstrap.servers': 'localhost:9092,localhost:9093'})
    sleep_time = 3
    try:
        while True:
            print('Sleeping for {0} seconds...'.format(sleep_time))
            time.sleep(sleep_time)
            list_of_orders = get_woocommerce_orders()
            produce_data(list_of_orders)
    except KeyboardInterrupt:
        pass

## Things to improve ##
# Make Woocommerce send request to Python script (Webhook on order create and update)