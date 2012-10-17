# _*_ encoding:utf-8 _*_
# author: 书记
# email: bh2[at]qq[dot]com

import json
import re
import urllib2
import sys
import os
from hashlib import md5

import poster

from netbase import Net

sys.path.append('.')
app_path = os.path.abspath(sys.path[-1]) + '/_3rdapp/CloudDisk360'

class CloudDisk(object):
    def __init__(self, email, pwd):
        # 对密码进行md5 hash
        self.pwd = md5(pwd).hexdigest()  
        self.email = email
        self.n = Net()
        self.login()
        self.upload()
        try:
            self.reward()
        except:
            pass

    def login(self):
        print self.email, 'login...'
        # 获取token:
        html = self.n.get('https://login.360.cn/?o=sso&m=getToken&func=QHPass.loginUtils.tokenCallback&userName=%s&rand=0.6075735737103969&callback=QiUserJsonP1348367367684' % self.email)
        token = eval(re.findall(r'(\{.*\})', html)[0])['token']

        # 登录360.cn：
        html = self.n.get('https://login.360.cn/?o=sso&m=login&from=i360&rtype=data&func=QHPass.loginUtils.loginCallback&userName=%s&pwdmethod=1&password=%s&isKeepAlive=1&token=%s&captFlag=&r=1348367489870&callback=QiUserJsonP1348367367685' % (self.email, self.pwd, token))

        # 得到用户信息和一个登录需要的s参数
        d = eval(re.findall(r'(\{.*\})', html)[0])
        self.userinfo = d['userinfo']  # 用户信息
        self.qid = self.userinfo['qid']

        # 由上一步得到一个s之后再登录yunpan.cn：
        self.n.get('http://rd.login.yunpan.cn/?o=sso&m=setcookie&func=QHPass.loginUtils.setCookieCallback&s=%s&callback=QiUserJsonP1348374391615' % d['s'])

        # 现在访问360主页就可以了：
        html = self.n.get('http://yunpan.360.cn/user/login?st=774')
        # 但是因为360使用了集群，所以访问上面这个网址他会自动转到另外一个网址
        self.cluster_id = re.findall(r'http://c(\d+).yunpan.360.cn', html[:1000])[0]

    def upload(self):
        print 'upload files*******************'
        '''上传文件'''
        # 先检查文件是否存在[这时会改变cookie]，同时获取存在于cookie中的token
        self.n.post('http://c%s.yunpan.360.cn/file/detectFileExists' % self.cluster_id, {
            'dir': '/', 'fname[]': 'upload-gorthon.txt', 'ajax': 1})
        # {"errno":0,"errmsg":"\u64cd\u4f5c\u6210\u529f","data":{"exists":[]}} 操作成功
        token = self.n.cookie.get('token')
        p = {'Filename': 'upload-gorthon.txt', 'path': '/',
                'qid': self.qid, 'ofmt': 'json', 'method': 'Sync.webUpload',
                'token': token, 'v': '1.0.1', 'file': open(app_path + '/upload-gorthon.txt', 'rb'),
                'Upload': 'Submit Query'}
        datagen, headers = poster.encode.multipart_encode(p)
        opener = poster.streaminghttp.register_openers()
        opener.add_handler(urllib2.HTTPCookieProcessor(self.n.cookie))
        i = 10
        while i:
            urllib2.urlopen(urllib2.Request('http://up%s.yunpan.360.cn/webupload' % self.cluster_id, datagen, headers)).read()
            # 分享刚才上传的文件
            # 要先得到刚才那个文件的nid
            print 'Upload file %s' % i
            jsn = self.n.post('http://c%s.yunpan.360.cn/file/list' % self.cluster_id,
                {'type': 2, 'order': 'asc', 'field': 'file_name', 't': '0.44758130819536746',
                    'path': '/', 'page': 0, 'page_size': 300, 'ajax': 1})
            nid = re.findall(r"\{oriName: 'upload-gorthon.txt',path: '/upload-gorthon.txt',nid: '(.*?)',.*?\}", jsn)[0]
            if i > 5:  # 分享5个文件
                self.n.post('http://c%s.yunpan.360.cn/link/create' % self.cluster_id,
                    {'nid': nid, 'name': '/upload-gorthon.txt', 'ajax': 1})
                print 'file %s was shared...' % i
            # 删除刚才上传的文件
            self.n.post('http://c%s.yunpan.360.cn/file/recycle/' % self.cluster_id, 
                    {'path[]': '/upload-gorthon.txt', 't': '0.5056146369315684'})
            print 'file %s was deleted...' % i
            i -= 1
        # 虽然刚才上传的文件删除了但是分享里面还存在，所以取消分享
        jsn = self.n.post('http://c%s.yunpan.360.cn/link/list' % self.cluster_id,
                {'type': 2, 'order': 'asc', 'field': 'file_name',
                    't': '0.44638799224048853', 'ajax': 1})
        print 'All files ware unshared...'
        nids = re.findall(r'nid":"(.*?)"', jsn)
        params = '&'.join(map(lambda x: 'nids[]=%s' % x, nids)) + '&ajax=1'
        self.n.post('http://c%s.yunpan.360.cn/link/cancel' % self.cluster_id, params)

    def reward(self):
        print 'Get reward************************'
        '''领取免费空间'''
        jsn = json.loads(self.n.post('http://c%s.yunpan.360.cn/user/signin/' % self.cluster_id, 
                dict(qid=self.qid, method='signin')
                ))

        data = jsn['data']
        print data
        total = int(data['total']) / 1024 ** 2  # 总共
        reward = int(data['reward']) / 1024 ** 2  # 奖励

def run():
    users = [('bh20077@126.com', '911198809'),
            ('511503686@qq.com', 'lianglei1213'),
            ('bh2@qq.com', 'Qyuytwqvbkcg11'),
            ]

    for email, pwd in users:
        CloudDisk(email, pwd)
