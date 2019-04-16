
import os
import sys

sys.path.append(os.path.join('/home/etl_montredo/data-pipeline-python-kafka'))

import global_configuration
from helpers import db_connection as db
from sqlalchemy import Column, String, Date, Numeric, DateTime, Integer



con_yml_dict = {
    'db_user': global_configuration.DwhPsql.db_user,
    'db_passwd': global_configuration.DwhPsql.db_passwd,
    'db_name': global_configuration.DwhPsql.db_name,
    'db_host': global_configuration.DwhPsql.db_host
}

db_conn = db.DBconnection(config_path=con_yml_dict, schema='woocommerce_en_de')
session = db_conn.get_session()
hash_id = db_conn.get_hash_id


class Orders(db_conn.get_base()):
    __tablename__ = 'orders'
    def __init__(self, **kwargs):
        if 'hash_id' not in kwargs:
            kwargs['hash_id'] = hash_id(kwargs['order_id'])
            self.id = kwargs['hash_id']
        super(Orders, self).__init__(**kwargs)

    hash_id = Column(String(32), primary_key=True)

    order_id = Column(String(5))
    date_created = Column(DateTime(timezone=False))
    date_modified = Column(DateTime(timezone=False))

    dwh_created_at = Column(DateTime(timezone=False), default=db_conn.get_date())
    dwh_updated_at = Column(DateTime(timezone=False), onupdate=db_conn.get_date())


def create_tables():
    db_conn.get_metadata().create_all()
