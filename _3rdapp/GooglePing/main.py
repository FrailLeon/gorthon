# _*_ encoding:utf-8 _*_
# author: 书记
# email: bh2[at]qq[dot]com

import urllib2

def run():
    return urllib2.urlopen('http://www.google.com/webmasters/tools/ping?sitemap=http://gorthon.sinaapp.com/sitemap.xml').read()
