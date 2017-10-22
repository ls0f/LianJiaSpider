# coding:utf-8

import gevent
from gevent import monkey
monkey.patch_all()
import pymysql
pymysql.install_as_MySQLdb()
from gevent.queue import Queue
from gevent.queue import Empty
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import metadata, Region, Xiaoqu, Chengjiao
from LianJiaSpider import do_xiaoqu_spider, xiaoqu_chengjiao_spider
from optparse import OptionParser

engine = create_engine('mysql://root@localhost/lianjia?charset=utf8', echo=False)

xiaoqu_queue = Queue(maxsize=20)
default_xiaoqu_thread = 10

metadata.create_all(engine)
Session = sessionmaker(bind=engine,  autoflush=True, autocommit=False)
# Session = scoped_session(sessionmaker(bind=engine,  autoflush=True, autocommit=False))


def xiaoqu_callback(res):
    session = Session()
    for item in res:
        xiaoqu = session.query(Xiaoqu).filter(Xiaoqu.href == item.href).first()
        if not xiaoqu:
            session.add(item)
            session.commit()


def get_all_xiaoqu():
    session = Session()
    regions = session.query(Region).filter(Region.status == 0).all()
    for item in regions:
        try:
            do_xiaoqu_spider(city=item.city, region=item.region, callback=xiaoqu_callback)
            item.status = 1
            session.add(item)
            session.commit()
        except KeyboardInterrupt:
            return
        except:
            import traceback
            print traceback.format_exc()


def add_region(city, region):
    session = Session()
    r = Region(city=city, region=region, status=0)
    session.add(r)
    session.commit()


def chengjiao_callback(res):
    session = Session()
    for item in res:
        if session.query(Chengjiao).filter(Chengjiao.href == item.href).first():
            pass
        else:
            print u"add 成交 小区:%s, 总价:%s, 均价:%s, 签约:%s" % (
                item.xiaoqu, item.total_price, item.unit_price, item.sign_time)
            session.add(item)
            session.commit()


def xiaoqu_worker(thread_no):
    session = Session()
    while 1:
        try:
            xiaoqu = xiaoqu_queue.get(timeout=5)
        except Empty:
            print u"thread[%s] finish" % thread_no
            break
        print u"thread[%s] 爬取 %s %s %s" % (thread_no, xiaoqu.region, xiaoqu.name, xiaoqu.href)
        try:
            xiaoqu_chengjiao_spider(xiaoqu.href, xiaoqu.region, chengjiao_callback)
            item = session.query(Xiaoqu).filter(Xiaoqu.id == xiaoqu.id).first()
            item.status = 1
            session.add(item)
            session.commit()
        except:
            import traceback
            print "thread[%s] %s " % (thread_no, traceback.format_exc())


def xiaoqu_boss(name=None):
    session = Session()
    q = session.query(Xiaoqu).filter(Xiaoqu.status == 0)
    if name:
        q = q.filter(Xiaoqu.name == name)
    for xiaoqu in q:
        xiaoqu_queue.put(xiaoqu)


def get_xiaoqu_chengjiao(worker_num=None, name=None):
    if worker_num is None:
        worker_num = default_xiaoqu_thread
    threads = [gevent.spawn(xiaoqu_boss, name)]
    for i in xrange(worker_num):
        threads.append(gevent.spawn(xiaoqu_worker, i + 1))

    gevent.joinall(threads)


if __name__ == "__main__":
    parse = OptionParser()
    parse.add_option('-a', '--add', help='add region', nargs=0)
    parse.add_option('-t', '--city', help='city(for add option)', nargs=1)
    parse.add_option('-r', '--region', help='region(for add option)', nargs=1)
    parse.add_option('-c', '--crawl', help='crawl chengjiao', nargs=0)
    parse.add_option('-w', '--worker', help='worker number', nargs=1, type=int)
    parse.add_option('-q', '--xiaoqu', help='xiaoqu name', nargs=1, default="")
    (options, args) = parse.parse_args()
    if options.add is not None:
        if options.city is None or options.region is None:
            parse.print_help()
            exit(1)
        add_region(options.city, options.region.decode("utf-8"))

    elif options.crawl is not None:
        get_all_xiaoqu()
        get_xiaoqu_chengjiao(options.worker, options.xiaoqu.decode("utf-8"))
    else:
        parse.print_help()
