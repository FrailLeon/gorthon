

#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os

import web
from web.contrib.template import render_jinja

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

import sae.const


urls = (
    '/(?:home/)?(?:page/(\d+))?', 'Home',  # 以发表日期查询，首页
    '/login', 'Login',
    '/logout', 'Logout',
    '/code_highlight', 'CodeHighlight',
    '/admin', 'Admin',
    '/post', 'PostArticle',
    '/edit(?:/(\d+))?', 'EditArticle',
    '/editor', 'Editor',
    '/add-classes', 'AddClasses',  # 添加分类
    '/comment', 'AddComment',
    '/article/home/(\d+)(?:/([-\w]+))?', 'ViewArticleFromHome',  # 从主页访问某一篇文章
    '/(\d{4}-\d{2})(?:/page/(\d+))?', 'QueryArticlesByDate',  # 以月份查询所有文章如所有在2012-02发表的文章
    u'/(translation|reprint|originality)(?:/page/(\d+))?', 'QueryType',  # 以类型【查询】所有文章如 翻译 | 转载 | 原创;page用于表示分页
    u'/article/(translation|reprint|originality)/(\d+)(?:/([-\w]+))?', 'ViewArticleFromType',  # 以类型【查看】某一文章
    '/article/(\d{4}-\d{2})/(\d+)(?:/([-\w]+))?', 'ViewArticleFromDate',  # 以月份查看文章如2012-02/10001/hello-world
    '/delete', 'DeleteArticle',
    u'/classes/([^/]+)', 'QueryClasses',
    '/backstage', 'Backstage',
    '/upload', 'Upload',
    '/delete/class/(\d+)', 'DeleteClass',
    '/change-pwd', 'ChangePwd',
    '/3rd/(\w+)', 'ThirdApp',
    '/sitemap.xml', 'Sitemap',  # sitemap
    '/.*?', 'Page404',
)


# 调试是否开启
debug = 'SERVER_SOFTWARE' not in os.environ
web.config.debug = debug


# 数据库配置
if debug:
    # 本地
    MYSQL_DB = 'app_gorthon'
    MYSQL_USER = 'shuji'
    MYSQL_PASS = '111'
    MYSQL_HOST_M = '127.0.0.1'
    MYSQL_HOST_S = '127.0.0.1'
    MYSQL_PORT = 3306
else:
    # SAE
    MYSQL_DB = sae.const.MYSQL_DB
    MYSQL_USER = sae.const.MYSQL_USER
    MYSQL_PASS = sae.const.MYSQL_PASS
    MYSQL_HOST_M = sae.const.MYSQL_HOST
    MYSQL_HOST_S = sae.const.MYSQL_HOST_S
    MYSQL_PORT = int(sae.const.MYSQL_PORT)


# sqlalchemy
# create_engine(数据库://用户名:密码(没有密码则为空)@主机名:端口/数据库名',echo =True)
mysql_engine = create_engine(
    'mysql://%s:%s@%s:%s/app_gorthon?charset=utf8' %
    (MYSQL_USER, MYSQL_PASS, MYSQL_HOST_M, MYSQL_PORT),
    encoding='utf8',
    echo=False,
    pool_recycle=5,
)
sql_session = scoped_session(sessionmaker(bind=mysql_engine))


def loadSqla(handler):
    try:
        sql_session.commit()
        return handler()
    except web.HTTPError:
        raise
    except Exception:
        sql_session.rollback()
    finally:
        sql_session.commit()


# jinja2模板加载
app_root = os.path.dirname(__file__)
templates_path = os.path.join(app_root, 'templates').replace('\\', '/')
render = render_jinja(
    templates_path,
    encoding='utf-8'
)


# webpy session
web.config.session_parameters = web.utils.storage({
    'cookie_name': 'session_id',
    'cookie_domain': None,
    'cookie_path': None,
    'timeout': 86400,  # 24 * 60 * 60, # 24 hours in seconds
    'ignore_expiry': True,
    'ignore_change_ip': True,
    'secret_key': 'fLjUfxqXtfNoIldA0A0J',
    'expired_message': 'Session expired',
    'httponly': True,
    'secure': False
})  # webpy cookbook和api文档里面都没有提到，可以看webpy的源码来进行设置
