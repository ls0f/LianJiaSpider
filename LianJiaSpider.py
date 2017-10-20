# -*- coding: utf-8 -*-
"""
@author: 冰蓝
@site: http://lanbing510.info
"""

import re
import urllib2  
import sqlite3
import random
import threading
from bs4 import BeautifulSoup
from datetime import datetime

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

TIMEOUT = 10

#登录，不登录不能爬取三个月之内的数据
import LianJiaLogIn


#Some User Agents
hds=[{'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},\
    {'User-Agent':'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},\
    {'User-Agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'},\
    {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0'},\
    {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36'},\
    {'User-Agent':'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},\
    {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},\
    {'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0'},\
    {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},\
    {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},\
    {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'},\
    {'User-Agent':'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11'},\
    {'User-Agent':'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'}]
    

def xiaoqu_spider(url_page):
    """
    爬取页面链接中的小区信息
    """
    try:
        req = urllib2.Request(url_page, headers=hds[random.randint(0,len(hds)-1)])
        source_code = urllib2.urlopen(req, timeout=TIMEOUT).read()
        plain_text= unicode(source_code)#,errors='ignore')
        soup = BeautifulSoup(plain_text)
    except (urllib2.HTTPError, urllib2.URLError), e:
        print e
        exit(-1)
    except Exception,e:
        print e
        exit(-1)
    
    xiaoqu_list=soup.findAll('div',{'class':'info-panel'})
    res = []
    for xq in xiaoqu_list:
        info_dict={}
        info_dict.update({'name':xq.find('a').text})
        content = unicode(xq.find('div',{'class':'con'}).renderContents().strip())
        info = re.match(r".+>(.+)</a>.+>(.+)</a>.+</span>(.+)<span>.+</span>(.+)",content)
        if info:
            info = info.groups()
            info_dict.update({'b_cite':info[0]})
            info_dict.update({'s_cite':info[1]})
            info_dict.update({'structure':info[2]})
            try:
                info_dict.update({'year':re.findall(r"(\d+)", info[3][:4])[0]})
            except IndexError as e:
                import traceback
                print traceback.format_exc()
                info_dict.update({'year': 0})

            res.append(info_dict)

    return res


def do_xiaoqu_spider(city, region):
    """
    爬取大区域中的所有小区信息
    """
    url=u"http://" + city +".lianjia.com/xiaoqu/rs"+region+"/"
    try:
        req = urllib2.Request(url, headers=hds[random.randint(0,len(hds)-1)])
        source_code = urllib2.urlopen(req,timeout=5).read()
        plain_text=unicode(source_code)#,errors='ignore')   
        soup = BeautifulSoup(plain_text)
    except (urllib2.HTTPError, urllib2.URLError), e:
        print e
        return
    except Exception,e:
        print e
        return
    d="d="+soup.find('div',{'class':'page-box house-lst-page-box'}).get('page-data')
    exec(d)
    total_pages=d['totalPage']
    
    threads=[]
    for i in range(total_pages):
        url_page= u"http://" + city + ".lianjia.com/xiaoqu/pg%drs%s/" % (i+1, region)
        t=threading.Thread(target=xiaoqu_spider,args=(city, url_page))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print u"爬下了 %s 区全部的小区信息" % region


def chengjiao_spider(url_page=u"http://bj.lianjia.com/chengjiao/pg1rs%E5%86%A0%E5%BA%AD%E5%9B%AD"):
    """
    爬取页面链接中的成交记录
    """
    try:
        req = urllib2.Request(url_page, headers=hds[random.randint(0,len(hds)-1)])
        source_code = urllib2.urlopen(req, timeout= TIMEOUT).read()
        plain_text=unicode(source_code)#,errors='ignore')   
        soup = BeautifulSoup(plain_text)
    except (urllib2.HTTPError, urllib2.URLError), e:
        print e
        exception_write('chengjiao_spider',url_page)
        return
    except Exception,e:
        print e
        exception_write('chengjiao_spider',url_page)
        return
    
    cj_list=soup.findAll('div',{'class':'info-panel'})
    res = []
    for cj in cj_list:
        info_dict={}
        href = cj.find('a')
        if not href:
            continue
        info_dict.update({'href':href.attrs['href']})
        content=cj.find('h2').text.split()
        if content:
            info_dict.update({'name':content[0]})
            info_dict.update({'fang_class':content[1]})
            info_dict.update({'structure': content[2]})
        content=unicode(cj.find('div',{'class':'con'}).renderContents().strip())
        content=content.split('/')
        if content:
            info_dict.update({'orientation':content[0].strip()})
            info_dict.update({'floor':content[1].strip()})
            if len(content)>=3:
                content[2]=content[2].strip();
                info_dict.update({'year':content[2][:4]})
        content=cj.findAll('div',{'class':'div-cun'})
        if content:
            info_dict.update({'sign_time': datetime.strptime(content[0].text, "%Y.%m.%d")})
            info_dict.update({'unit_price': re.findall(r"(\d+)",content[1].text)[0]})
            info_dict.update({'total_price':re.findall(r"(\d+\.?\d+)" ,content[2].text)[0]})
        content=cj.find('div',{'class':'introduce'}).text.strip().split()
        if content:
            for c in content:
                if c.find(u'满')!=-1:
                    info_dict.update({'fang_class':c})
                elif c.find(u'学')!=-1:
                    info_dict.update({'school': c})
                elif c.find(u'距')!=-1:
                    info_dict.update({'sub_way': c})
        
        res.append(info_dict)
    return res


def xiaoqu_chengjiao_spider(city, xq_name=u"冠庭园"):
    """
    爬取小区成交记录
    """
    url=u"http://" + city + ".lianjia.com/chengjiao/rs"+urllib2.quote(xq_name)+"/"
    try:
        req = urllib2.Request(url,headers=hds[random.randint(0,len(hds)-1)])
        source_code = urllib2.urlopen(req,timeout=10).read()
        plain_text=unicode(source_code)#,errors='ignore')   
        soup = BeautifulSoup(plain_text)
    except (urllib2.HTTPError, urllib2.URLError), e:
        print e
        exception_write('xiaoqu_chengjiao_spider',xq_name)
        return
    except Exception,e:
        print e
        exception_write('xiaoqu_chengjiao_spider',xq_name)
        return
    content=soup.find('div',{'class':'page-box house-lst-page-box'})
    total_pages=0
    if content:
        d="d="+content.get('page-data')
        exec(d)
        total_pages=d['totalPage']
    
    threads=[]
    for i in range(total_pages):
        url_page=u"http://" + city + ".lianjia.com/chengjiao/pg%drs%s/" % (i+1,urllib2.quote(xq_name))
        t=threading.Thread(target=chengjiao_spider,args=(url_page))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    
def do_xiaoqu_chengjiao_spider(db_xq,db_cj):
    """
    批量爬取小区成交记录
    """
    count=0
    xq_list=db_xq.fetchall()
    for xq in xq_list:
        xiaoqu_chengjiao_spider(db_cj,xq[0])
        count+=1
        print 'have spidered %d xiaoqu' % count
    print 'done'




if __name__=="__main__":

    #爬下所有的小区信息
    for region in regions:
        do_xiaoqu_spider(db_xq, region)
    
    #爬下所有小区里的成交信息
    do_xiaoqu_chengjiao_spider(db_xq,db_cj)

    #重新爬取爬取异常的链接
    exception_spider(db_cj)

