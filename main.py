# coding:utf-8

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import metadata, Region, Xiaoqu, Chengjiao
import time

engine = create_engine('sqlite:///./lianjia.db', echo=False)
from Queue import Queue
from Queue import Empty,Full
import threading
from optparse import OptionParser

xiaoqu_queue = Queue(maxsize=20)

default_xiaoqu_thread = 10

metadata.create_all(engine )
Session = scoped_session(sessionmaker(bind=engine,  autoflush=True, autocommit=False))

session_dict = {}


def get_session():
    return Session()
    '''
    tid = threading.current_thread().ident
    if tid not in session_dict:
        session = Session()
        session_dict[tid] = session
    return session_dict[tid]
    '''

from LianJiaSpider import do_xiaoqu_spider, xiaoqu_chengjiao_spider


def xiaoqu_callback(res):
    session = get_session()
    for item in res:
        xiaoqu = session.query(Xiaoqu).filter(Xiaoqu.href == item.href).first()
        if not xiaoqu:
            session.add(item)
            session.commit()


def get_all_xiaoqu():
    session = get_session()
    regions = session.query(Region).filter(Region.status == 0).all()
    for item in regions:
        try:
            do_xiaoqu_spider(city=item.city, region=item.region, callback=xiaoqu_callback)
            xiaoqu = session.query(Xiaoqu).fiter(Xiaoqu.id == item.id).first()
            xiaoqu.status = 1
            session.add(xiaoqu)
            session.commit()
        except KeyboardInterrupt:
            return
        except:
            import traceback
            print traceback.format_exc()


def add_region(city, region):
    session = get_session()
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
    threads = [threading.Thread(target=xiaoqu_boss, args=(name, ))]
    for i in xrange(worker_num):
        threads.append(threading.Thread(target=xiaoqu_worker, args=(i + 1,)))
    for th in threads:
        th.start()
    for th in threads:
        while True:
            try:
                th.join(2)
                time.sleep(2)
                if not th.isAlive():
                    break
            except KeyboardInterrupt:
                exit(1)


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
