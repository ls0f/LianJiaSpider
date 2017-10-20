# coding:utf-8


from models import metadata
from sqlalchemy import create_engine


engine = create_engine('sqlite:///./lianjia.db', echo=True)

metadata.create_all(engine)
