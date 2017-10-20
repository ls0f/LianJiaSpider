# coding:utf-8


from datetime import datetime

from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.schema import MetaData, UniqueConstraint
from sqlalchemy import (Column, DateTime, String, Integer, Float, Date)

metadata = MetaData()


@as_declarative(metadata=metadata)
class Base(object):
    """
    base type for all sqlalchemy mapped types
    """
    id = Column(Integer, autoincrement=True, primary_key=True)
    create_time = Column(DateTime, nullable=False, default=datetime.now)
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class Region(Base):
    __tablename__ = 'region'
    __table_args__ = (
        UniqueConstraint("city", "region", name="city_region_unique"),
    )
    city = Column(String(10), nullable=False)
    region = Column(String(20), nullable=False)
    ch_city = Column(String(20), nullable=False, default="")


class Xiaoqu(Base):
    __tablename__ = 'xiaoqu'
    __table_args__ = (
        UniqueConstraint("region_id", "name", name="region_name_unique"),
    )
    region_id = Column(Integer, nullable=False)
    region = Column(String(20), nullable=False)
    city = Column(String(10), nullable=False)
    name = Column(String(20), nullable=False)
    b_cite = Column(String(20), nullable=False)
    s_cite = Column(String(20), nullable=False)
    structure = Column(String(20), nullable=False)
    year = Column(Integer, nullable=False)


class Chengjiao(Base):

    __tablename__ = 'chengjiao'
    __table_args__ = (
        UniqueConstraint("href", name="href_unique"),
    )
    href = Column(String(50), nullable=False)
    region = Column(String(20), nullable=False)
    city = Column(String(10), nullable=False)
    name = Column(String(20), nullable=False)
    structure = Column(String(20), nullable=False)
    area = Column(Float, nullable=False)
    orientation = Column(String(20), nullable=False, default="")
    floor = Column(String(20), default="")
    year = Column(Integer, nullable=False)
    sign_time = Column(Date, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    fang_class = Column(String(20), default="")
    school = Column(String(20), default="")
    subway = Column(String(100), default="")
