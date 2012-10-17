

#!/usr/bin/python
#-*- coding: utf-8 -*-

import datetime
import urllib2
import urllib
import json
import re
import cookielib
from sgmllib import SGMLParser
from xml.parsers.expat import ParserCreate
from models import Article

try:  # 本地
    import Image
except ImportError:  # sae
    from PIL import Image
import web
from sqlalchemy import desc

from settings import sql_session
from models import Ip, func


class SQLAStore(web.session.Store):
    def __init__(self, table):
        self.table = table

    def __contains__(self, key):
        return bool(sql_session.execute(self.table.select(self.table.c.session_id == key)).fetchone())

    def __getitem__(self, key):
        s = sql_session.execute(self.table.select(self.table.c.session_id == key)).fetchone()
        if s is None:
            raise KeyError
        else:
            sql_session.execute(self.table.update().values(atime=datetime.datetime.now()).where(self.table.c.session_id == key))
            return self.decode(s[self.table.c.data])

    def __setitem__(self, key, value):
        pickled = self.encode(value)
        if key in self:
            sql_session.execute(self.table.update().values(data=pickled).where(self.table.c.session_id == key))
        else:
            sql_session.execute(self.table.insert().values(session_id=key, data=pickled))
        sql_session.commit()

    def __delitem__(self, key):
        sql_session.execute(self.table.delete(self.table.c.session_id == key))

    def cleanup(self, timeout):
        timeout = datetime.timedelta(timeout / (24.0 * 60 * 60))
        last_allowed_time = datetime.datetime.now() - timeout
        sql_session.execute(self.table.delete(self.table.c.atime < last_allowed_time))


class Net(object):
    """
    网络工具,带Cookie
    """
    def __init__(self):
        self.cookie = cookielib.LWPCookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.168 Safari/535.19'}
        urllib2.install_opener(self.opener)

    def post(self, url, params):
        return self.opener.open(urllib2.Request(url, urllib.urlencode(params), self.headers), timeout=30).read()

    def get(self, url):
        return self.opener.open(urllib2.Request(url, headers=self.headers), timeout=30).read()


def saveIp(ip):
    """
    ip统计，将ip的地点入库; sina的api
    """
    if web.config.debug:
        d = {'country': u'书记', 'province': u'书记', 'city': u'书记'}
    else:
        url = 'http://int.dpool.sina.com.cn/iplookup/iplookup.php?format=json&ip=%s' % ip
        d = json.loads(urllib2.urlopen(url).read())
    try:
        position = d['country'] + '@' + d['province'] + '@' + d['city']
    except KeyError:
        position = '@@'
    try:
        city = sql_session.query(Ip).filter_by(ip=ip)[0]
        city.visit += 1
    except IndexError:
        city = Ip(ip, 1, position)
        sql_session.add(city)
    sql_session.commit()
    return d['city']


def getIpStatics():
    q = sql_session.query(Ip)
    top_city = q.order_by(desc(Ip.visit))[0]
    total_visit = int(sql_session.query(func.sum(Ip.visit)).scalar())
    return dict(
        ip_count=q.count(),
        top_ip=top_city.ip,
        top_num=top_city.visit,
        top_pos=top_city.position,
        total_visit=total_visit,
    )


def pageArticles(articles, page=1, per_page=5):
    """
    分页
    @articles: 文章, 如果是列表则直接操作，如果是查询就先查询
    @page: 总共分多少页;
    @per_page: 每页多少篇
    """
    if not isinstance(articles, list):
        articles = articles()
    num = 10 if per_page > 10 else per_page
    end = int(page) * num
    start = end - num
    return len(articles), articles[start:end]


def googleTranslate(s):
    try:
        html = Net().get(
            "http://translate.google.cn/translate_a/t?client=t&text=%s&hl=en&sl=zh-CN&"
            "tl=en&multires=1&trs=1&srcrom=1&prev=btn&ssel=0&tsel=0&sc=1" % urllib.quote(str(s)))
        index = html.index("]")
        return re.sub(r"-+", "-", re.sub(r"[^\w-]+", "", re.findall(r"(.*?),", html[3:index])[0].replace(" ", "-"))).lower()
    except Exception:
        return None


class _Html2text(SGMLParser):
    def reset(self):
        self.text = ''
        SGMLParser.reset(self)

    def handle_data(self, text):
        self.text += text


def html2text(html):
    parser = _Html2text()
    parser.feed(html)
    parser.close()
    return parser.text


def getMultimedia(html):
    # 先判断有没有视频
    media = re.search(r'(<embed.*?/>)', html)
    if media:
        media = media.group()
    else:  # 判断有没有图片
        media = re.search(r'(<img.*?/>)', html)
        media = media.group() if media else ''
    media = '<p style="z-index: 0;text-align:center;">' + media + '<br /></p>' if media else ''
    return media


class Xml2Json:
    LIST_TAGS = ['COMMANDS']

    def __init__(self, data=None):
        self._parser = ParserCreate()
        self._parser.StartElementHandler = self.start
        self._parser.EndElementHandler = self.end
        self._parser.CharacterDataHandler = self.data
        self.result = None
        if data:
            self.feed(data)
            self.close()

    def feed(self, data):
        self._stack = []
        self._data = ''
        self._parser.Parse(data, 0)

    def close(self):
        self._parser.Parse("", 1)
        del self._parser

    def start(self, tag, attrs):
        assert attrs == {}
        assert self._data.strip() == ''
        self._stack.append([tag])
        self._data = ''

    def end(self, tag):
        last_tag = self._stack.pop()
        assert last_tag[0] == tag
        if len(last_tag) == 1:  # leaf
            data = self._data
        else:
            if tag not in Xml2Json.LIST_TAGS:
                data = {}
                for k, v in last_tag[1:]:
                    if k not in data:
                        data[k] = v
                    else:
                        el = data[k]
                        if type(el) is not list:
                            data[k] = [el, v]
                        else:
                            el.append(v)
            else:  # force into a list
                data = [{k:v} for k, v in last_tag[1:]]
        if self._stack:
            self._stack[-1].append((tag, data))
        else:
            self.result = {tag: data}
        self._data = ''

    def data(self, data):
        self._data = data


def getWeather(city=u'南京'):
    """
    新浪天气预报
    """
    url = 'http://php.weather.sina.com.cn/xml.php?city=%s&password=DJOYnieT8234jlsK&day=0' % city
    url = url.encode('gbk')
    xml = urllib2.urlopen(url, timeout=15).read()
    return Xml2Json(xml).result['Profiles']['Weather']


def resizeImg(img, size=None, min_width=705):
    """缩放图片"""
    w, h = img.size
    if size is None:
        size = min_width, int(h / (w * 1. / min_width))
        img = img.resize(size, Image.ANTIALIAS)  # 滤镜输出，不然缩放质量很差
    return img


def sitemap():
    html = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset
      xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
            http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
%s
</urlset>
    '''
    articles = sql_session.query(Article).order_by(Article.date.desc()).all()
    res = ['''<url>
    <loc>http://gorthon.sinaapp.com</loc>
    <changefreq>always</changefreq>
    <lastmod>%s+08:00</lastmod>
    <priority>1.00</priority>
</url>''' % articles[0].date.strftime('%Y-%m-%dT%H:%M:%S')]
    for a in articles:
        url = a.url
        aid = a.aid
        date = a.date.strftime('%Y-%m-%dT%H:%M:%S')
        if url is not None:
            aid = '%s/%s' % (aid, url)
        res.append('''
<url>
    <loc>http://gorthon.sinaapp.com/article/home/%s</loc>
    <changefreq>monthly</changefreq>
    <lastmod>%s+08:00</lastmod>
    <priority>0.8</priority>
</url>''' % (aid, date))
    return html % ''.join(res)

if __name__ == "__main__":
    print googleTranslate("Gorthon | Google将推出收费版本的Translate API")
