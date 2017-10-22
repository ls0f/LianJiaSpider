# coding:utf-8

import pymysql

pymysql.install_as_MySQLdb()

from models import metadata
from sqlalchemy import create_engine


engine = create_engine('mysql://root@localhost/lianjia', echo=True)

metadata.create_all(engine)
