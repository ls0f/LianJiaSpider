# -*- coding: utf-8 -*-
"""
@author: 冰蓝
@site: http://lanbing510.info
"""

import re
import urlparse
import urllib2
import json
import random
import threading
from bs4 import BeautifulSoup
from datetime import datetime
from models import Chengjiao, row2dict, Xiaoqu


TIMEOUT = 10

# 登录，不登录不能爬取三个月之内的数据
import LianJiaLogIn


# Some User Agents
hds = [{'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}, \
       {
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'}, \
       {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'}, \
       {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0'}, \
       {
           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36'}, \
       {
           'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'}, \
       {
           'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'}, \
       {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0'}, \
       {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'}, \
       {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'}, \
       {
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'}, \
       {'User-Agent': 'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11'}, \
       {'User-Agent': 'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'}]


def xiaoqu_spider(region, url_page):
    """
    爬取页面链接中的小区信息
    """
    p = urlparse.urlparse(url_page)
    city = p.hostname.split(".")[0]
    req = urllib2.Request(url_page.encode("utf-8"), headers=hds[random.randint(0, len(hds) - 1)])
    plain_text = urllib2.urlopen(req, timeout=TIMEOUT).read()
    soup = BeautifulSoup(plain_text, "html.parser")
    xiaoqu_list = soup.find('ul', {'class': 'listContent'}).find_all("li")
    res = []
    for xq in xiaoqu_list:
        obj = Xiaoqu(city=city, region=region)
        obj.href = xq.find('div', {"class": "title"}).find("a").attrs['href']
        obj.name = xq.find('div', {"class": "title"}).find("a").text
        position_info = xq.find("div", {"class": "positionInfo"}).find_all("a")
        position_text = xq.find("div", {"class": "positionInfo"}).text
        if len(position_info) >= 1:
            obj.b_cite = position_info[0].text
        if len(position_info) >= 2:
            obj.s_cite = position_info[1].text

        year = re.findall(u"(\d+)年", position_text)
        if year:
            obj.year = year[0]

        res.append(obj)
    return res


def do_xiaoqu_spider(city, region, callback=None):
    """
    爬取大区域中的所有小区信息
    """
    url = u"http://" + city + ".lianjia.com/xiaoqu/rs" + region + "/"
    req = urllib2.Request(url.encode("utf-8"), headers=hds[random.randint(0, len(hds) - 1)])
    plain_text = urllib2.urlopen(req, timeout=TIMEOUT).read()
    soup = BeautifulSoup(plain_text, "html.parser")
    page_box = json.loads(soup.find('div', {'class': 'page-box house-lst-page-box'}).get("page-data"))
    total_page = page_box["totalPage"]
    for i in xrange(total_page):
        print u"正在爬取 %s %s %d页" % (city, region, i+1)
        url_page = u"http://" + city + ".lianjia.com/xiaoqu/pg%drs%s/" % (i+1, region)
        print url_page
        res = xiaoqu_spider(region, url_page)
        if callback:
            callback(res)
            print "爬取记录 %s" % len(res)

    print u"爬下了 %s 区全部的小区信息" % region


def chengjiao_spider(url_page=u"http://bj.lianjia.com/chengjiao/pg1rs%E5%86%A0%E5%BA%AD%E5%9B%AD", region=None):
    """
    爬取页面链接中的成交记录
    """
    p = urlparse.urlparse(url_page)
    city = p.hostname.split(".")[0]
    req = urllib2.Request(url_page, headers=hds[random.randint(0, len(hds) - 1)])
    plain_text = urllib2.urlopen(req, timeout=TIMEOUT).read()
    soup = BeautifulSoup(plain_text, "html.parser")
    cj_list = soup.find('ul', {'class': 'listContent'}).find_all('li')
    res = []
    for cj in cj_list:
        obj = Chengjiao(city=city, region=region or "")
        href = cj.find('a')
        if not href:
            continue
        obj.href = href.attrs['href']
        content = cj.find('div', {'class': "title"}).text.split()
        obj.xiaoqu = content[0]
        obj.structure = content[1]
        try:
            obj.area = re.findall(r"(\d+\.?\d+)", content[2])[0]
        except IndexError:
            continue
        house_info = cj.find('div', {"class": "houseInfo"}).text.strip().split("|")
        try:
            obj.orientation = house_info[0]
            obj.fit_up = house_info[1]
            obj.lift = house_info[2]
        except IndexError:
            pass
        deal_date = cj.find('div', {'class': "dealDate"}).text.strip()
        if u"成交" in deal_date:
            print u"最近30天成交"
            continue
        try:
            obj.sign_time = datetime.strptime(deal_date, "%Y.%m.%d")
        except ValueError:
            obj.sign_time = datetime.strptime(deal_date, "%Y.%m")

        try:
            obj.total_price = cj.find('div', {'class': "totalPrice"}).find("span", {"class": "number"}).text
        except AttributeError:
            print cj.find('div', {'class': "totalPrice"}).text
            continue
        if '*' in obj.total_price:
            continue
        floor = cj.find("div", {"class": "positionInfo"}).get_text().strip().split()
        try:
            obj.floor = floor[0]
            obj.year = re.findall(r"(\d+)", floor[1])[0]
        except IndexError:
            pass
        obj.unit_price = cj.find('div', {'class': "unitPrice"}).find("span", {"class": "number"}).text
        house_txt = cj.find("span", {"class": "dealHouseTxt"})
        if house_txt:
            obj.house_txt = house_txt.get_text()

        cycle_txt = cj.find("div", {"class": "dealCycleeInfo"})
        if cycle_txt:
            obj.cycle_info = cycle_txt.get_text()
            expect = re.findall(u"(\d+)万", obj.cycle_info)
            if expect:
                obj.expect_price = expect[0]
            deal = re.findall(u"(\d+)天", obj.cycle_info)
            if deal:
                obj.deal_days = deal[0]

        res.append(obj)

    return res


def xiaoqu_chengjiao_spider(xiaoqu_href, region, callback=None):
    """
    爬取小区成交记录
    """
    p = urlparse.urlparse(xiaoqu_href)
    xiqoqu_id = re.findall(r"(\d+)", xiaoqu_href)[0]
    url = "http://%s/chengjiao/c%s" % (p.hostname, xiqoqu_id)
    req = urllib2.Request(url, headers=hds[random.randint(0, len(hds) - 1)])
    plain_text = urllib2.urlopen(req, timeout=10).read()
    soup = BeautifulSoup(plain_text, "html.parser")
    try:
        page_box = json.loads(soup.find('div', {'class': 'page-box house-lst-page-box'}).get("page-data"))
        total_page = page_box["totalPage"]
    except AttributeError:
        return
    for i in range(total_page):
        url_page = "http://%s/chengjiao/pg%dc%s" % (p.hostname, i+1, xiqoqu_id)
        print u"正在爬取 %d/%d %s" % (i+1, total_page, url_page)
        res = chengjiao_spider(url_page, region)
        if callback:
            callback(res)


if __name__ == "__main__":
    pass
