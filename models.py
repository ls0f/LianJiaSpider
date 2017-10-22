# coding:utf-8


from datetime import datetime

from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.schema import MetaData, UniqueConstraint
from sqlalchemy import (Column, DateTime, String, Integer, Float, Date)


def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = getattr(row, column.name)

    return d

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
    city = Column(String(8), nullable=False)
    region = Column(String(32), nullable=False)
    ch_city = Column(String(32), nullable=False, default="")
    status = Column(Integer, nullable=False, default=0)


class Xiaoqu(Base):
    __tablename__ = 'xiaoqu'
    __table_args__ = (
        UniqueConstraint("href", name="href_unique"),
    )
    href = Column(String(128), nullable=False)
    region = Column(String(32), nullable=False)
    city = Column(String(8), nullable=False)
    name = Column(String(32), nullable=False)
    b_cite = Column(String(32), nullable=False, default="")
    s_cite = Column(String(32), nullable=False, default="")
    year = Column(Integer, nullable=False, default=0)
    status = Column(Integer, nullable=False, default=0)


class Chengjiao(Base):

    __tablename__ = 'chengjiao'
    __table_args__ = (
        UniqueConstraint("href", name="href_unique"),
    )
    href = Column(String(64), nullable=False)
    region = Column(String(32), nullable=False)
    city = Column(String(8), nullable=False)
    xiaoqu = Column(String(32), nullable=False)
    orientation = Column(String(32), nullable=False, default="")
    fit_up = Column(String(32), nullable=False, default="")
    lift = Column(String(32), nullable=False, default="")
    structure = Column(String(32), nullable=False)
    area = Column(Float, nullable=False)
    floor = Column(String(32), default="")
    year = Column(Integer, nullable=False, default=0)
    sign_time = Column(Date, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    house_txt = Column(String(512), nullable=False, default="")
    cycle_info = Column(String(512), nullable=False, default="")
    expect_price = Column(Integer, nullable=False, default=0)
    deal_days = Column(Integer, nullable=False, default=0)
