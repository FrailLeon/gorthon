# _*_ encoding:utf-8 _*_
# author: 书记
# email: bh2[at]qq[dot]com

import urllib2
import urllib
import cookielib
import re

class Net(object):
    def __init__(self):
        self.cookie = cookielib.LWPCookieJar()
        self.cookie.get = self._getCookie
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1'}
        urllib2.install_opener(self.opener)

    def post(self, url, params):
        if isinstance(params, dict):
            params = urllib.urlencode(params)
        return self.opener.open(urllib2.Request(url, params, self.headers), timeout=120).read().decode('u8')

    def get(self, url):
        return self.opener.open(urllib2.Request(url, headers=self.headers), timeout=120).read().decode('u8')

    def _getCookie(self, name):
        for i in self.cookie:
            if i.name == name:
                return i.value
