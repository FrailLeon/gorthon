#!/usr/bin/python
#-*- coding: utf-8 -*-

import json
import hashlib
import datetime
import random
import StringIO

import pygments
from  pygments.lexers import guess_lexer_for_filename
from  pygments.formatters import HtmlFormatter
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy.exc import InvalidRequestError

import web
import sae
import sae.storage

from settings import urls, loadSqla, render, sql_session
from models import Lol, webpy_table, Classes, initDb, Article, func, Comment
from utils import (
    SQLAStore, saveIp, getIpStatics, pageArticles, googleTranslate, html2text,
    resizeImg, Image, getMultimedia, sitemap
)

render._lookup.filters['html2text'] = html2text
render._lookup.filters['getMultimedia'] = getMultimedia


def needLogin(func):
    def inner(*args):
        _dealIp()
        if session.get('logged', False):
            return func(*args)
        web.header("Content-Type", "text/html")
        raise web.notfound(render.page404())
    return inner


def _dealIp():
    if web.ctx.ip == '127.0.0.1':
        web.ctx.ip = '121.229.180.132'
    if  session.get('_ip', None) is None:
        session['_city'] = saveIp(web.ctx.ip)
        session['_ip'] = web.ctx.ip


class Sitemap:
    def GET(self):
        web.header("Content-Type", "text/xml")
        return sitemap()


class Home:
    def GET(self, page):
        if page is None:
            page = 1
        # ip计数
        _dealIp()
        # ip统计
        statics = getIpStatics()

        # 得到最近10篇文章
        per_page = 5
        post_count, statics['articles'] = pageArticles(
            lambda: sql_session.query(Article).order_by(
                Article.date.desc()
            ).all(), page, per_page)
        # 所有分类
        statics['all_classes'] = dict(sql_session.query(
            Classes.id, Classes.cls).order_by(Classes.id).all())
        # 文章总数，用于分页
        statics['post_count'] = post_count
        statics['per_page'] = per_page

        statics['now'] = datetime.datetime.now()
        statics['request'] = 'home'

        #parser = html2text()
        #statics['parser'] = parser
        # 得到评论数
        for i in statics['articles']:
            i.comment_num = len(sql_session.query(Comment).filter(
                Comment.aid == i.aid).all())

        statics['logged'] = session.get('logged', False)
        web.header("Content-Type", "text/html")
        return render.home(statics)


class Page404:
    def GET(self):
        _dealIp()
        web.header("Content-Type", "text/html")
        raise web.notfound(render.page404())


class CodeHighlight:
    def POST(self):
        _dealIp()
        i = web.input(type='.py', code='#! usr/bin/env python')
        code = i.code
        lexer = guess_lexer_for_filename('code' + i.type, code)
        html = pygments.highlight(code, lexer, HtmlFormatter(linenos=True))
        web.header("Content-Type", "application/json")
        return json.dumps(dict(html=html))


class Login:
    """
    Ajax调用，登录
    """
    def POST(self):
        pwd = web.input(lol='').lol
        session['logged'] = False
        if pwd:
            pwd = hashlib.sha1(pwd).hexdigest()
            try:
                lol = sql_session.query(Lol)[0].lol
            except IndexError:
                lol = None
            if pwd == lol:
                session['logged'] = True
        web.header("Content-Type", "application/json")
        return json.dumps(dict(lol=session.logged))


class Logout:
    """
    注销登录，清除session
    """
    def GET(self):
        _dealIp()
        session['logged'] = False
        session.kill()
        raise web.seeother('/')


class Admin:
    """
    Ajax调用，返回发表文章及注销页面
    """
    @needLogin
    def GET(self):
        web.header("Content-Type", "text/html")
        return render.admin()


class EditArticle:
    """
    加载发表文章页面
    """
    @needLogin
    def GET(self, id):
        article = None
        # 编辑已有文章:
        if id is not None:
            article = sql_session.query(Article).filter(
                Article.aid == id).first()
            if article is None:
                raise web.notfound(render.page404())
        classes = sql_session.query(Classes).order_by(Classes.id).all()
        statics = _formatStatics()
        statics['classes'] = classes
        statics['article'] = article
        web.header("Content-Type", "text/html")
        return render.edit(statics)


class PostArticle:
    """
    新增文章或者更新文章
    """
    @needLogin
    def POST(self):
        i = web.input(
            operation='save', title='', content='', tags='', type=u'原创',
            classes=u'默认分类', origin='', announcement='', pwd=False,
            reviewable=True, reproduced=True
        )
        title = i.title
        content = i.content
        msg = (title == '') and u"请输入标题" or ((content == '') and u"请输入内容" or "ok")
        if msg == 'ok':
            tags = i.tags
            type = i.type
            classes = i.classes
            origin = i.origin
            announcement = i.announcement
            pwd = i.pwd == 'true'
            reviewable = i.reviewable == 'true'
            reproduced = i.reproduced == 'true'
            url = googleTranslate(title.encode("u8"))
            operation = i.operation
            aid = i.aid
            if operation == "save":  # 保存
                article = sql_session.query(Article).filter(
                    Article.aid == aid).first()
                article.title = title
                article.tags = tags
                article.classes = classes
                article.origin = origin
                article.announcement = announcement
                article.reproduced = reproduced
                article.reviewable = reviewable
                article.url = url
                article.pwd = pwd
                article.content = content
                try:
                    sql_session.commit()
                    msg = u'保存成功'
                except Exception, e:
                    msg = e
            elif operation == 'submit':  # 发表
                article = Article(
                    title=title,
                    content=content,
                    classes=classes,
                    type=type,
                    pwd=pwd,
                    reviewable=reviewable,
                    reproduced=reproduced,
                    tags=tags,
                    origin=origin,
                    announcement=announcement,
                    url=url,
                    date=datetime.datetime.now()
                )
                sql_session.add(article)
                try:
                    sql_session.commit()
                    msg = u'发表成功'
                except Exception, e:
                    msg = e
            elif operation == 'preview':  # 预览
                msg = u'预览'
        web.header("Content-Type", "application/json")
        return json.dumps(dict(msg=msg))


class AddComment:
    """添加评论"""
    def POST(self):
        _dealIp()
        i = web.input()
        pid = i.pid if i.pid else None
        if i.type == 'add':  # 添加评论
            sql_session.add(Comment(
                aid=i.aid,
                pid=pid,
                url=i.url,
                author=i.nick if i.nick else '',
                content=i.content,
                mail=i.mail)
            )
            sql_session.commit()

        web.header("Content-Type", "application/json")
        return json.dumps(dict(msg='ok'))


class AddClasses:
    """
    添加自定义分类
    """
    @needLogin
    def POST(self):
        id = web.input(id=None).id
        ret = {}
        classes = [i for i in web.input(cls='').cls.split() if i]
        try:
            if id is not None and int(id) == 1:
                raise Exception
            if id is None:  # 添加分类
                for cls in classes:
                    if (not cls.startswith(u'空格分隔')) and sql_session.query(
                        Classes.id
                    ).filter(
                            Classes.cls == cls
                    ).first() is None:  # 不存在就添加
                        sql_session.add(Classes(cls=cls))
                        id = sql_session.query(Classes.id).filter(
                            Classes.cls == cls).first().id  # 返回添加的id
                        ret[id] = cls
            else:  # 修改分类
                cls = sql_session.query(Classes).filter(
                    Classes.id == id).first()
                if len(classes[0]) > 15:
                    raise InvalidRequestError
                ret[id] = cls.cls = classes[0]
            sql_session.commit()
        except InvalidRequestError:
            ret['-1'] = '每个分类的长度不能超过15'
        except Exception:
            ret["-1"] = '不能修改[默认分类]'
        web.header("Content-Type", "application/json")
        return json.dumps(ret)


def _getArticleByAid(aid):
    article = sql_session.query(Article).filter(Article.aid == aid).first()
    if article is None:
        raise web.notfound(render.page404())
    article.pv += 1  # 浏览量 + 1
    article.comment = sql_session.query(Comment).filter(
        Comment.aid == aid).all()
    article.comment_num = len(article.comment)
    return article


def _formatStatics():
    statics = getIpStatics()
    statics['logged'] = session.get('logged', False)
    statics['now'] = datetime.datetime.now()
    return statics


class ViewArticleFromHome:
    """
    浏览单篇文章，从主页访问时，仅以发表时间确定下一篇和上一篇
    """
    def GET(self, aid, url):
        _dealIp()
        article = _getArticleByAid(aid)
        prev_article = sql_session.query(
            Article.aid,
            Article.title,
            Article.url
        ).filter(
            Article.date < article.date
        ).order_by(Article.date.desc()).first()
        next_article = sql_session.query(
            Article.aid,
            Article.title,
            Article.url).filter(
                Article.date > article.date
            ).order_by(Article.date.asc()).first()

        statics = _formatStatics()
        statics['article'] = article
        statics['prev'] = prev_article
        statics['next'] = next_article
        statics['request'] = 'home'

        web.header("Content-Type", "text/html")
        return render.article(statics)


class ViewArticleFromType:
    """
    浏览单篇文章，从分类访问时，以发表时间和分类确定下一篇和上一篇
    """
    def GET(self, type, aid, url):
        _dealIp()
        article = _getArticleByAid(aid)
        t = u"翻译" if type == "translation" else (
            u"原创" if type == "originality" else u"转载")
        prev_article = sql_session.query(
            Article.aid,
            Article.title,
            Article.url
        ).filter(
            Article.date < article.date
        ).filter(Article.type == t).order_by(Article.date.desc()).first()
        next_article = sql_session.query(
            Article.aid,
            Article.title,
            Article.url
        ).filter(
            Article.date > article.date
        ).filter(Article.type == t).order_by(Article.date.asc()).first()

        statics = _formatStatics()
        statics['article'] = article
        statics['prev'] = prev_article
        statics['next'] = next_article
        statics['request'] = type

        web.header("Content-Type", "text/html")
        return render.article(statics)


class ViewArticleFromDate:
    """
    浏览单篇文章，从日期访问时，以发表时间和给定日期确定下一篇和上一篇
    """
    def GET(self, date, aid, url):
        _dealIp()
        article = _getArticleByAid(aid)
        year, month = map(int, date.split("-"))
        d = Article.__table__.c.date
        prev_article = sql_session.query(
            Article.aid,
            Article.title,
            Article.url
        ).filter(
            Article.date < article.date
        ).filter(func.month(d) == month).filter(
            func.year(d) == year
        ).order_by(Article.date.desc()).first()
        next_article = sql_session.query(
            Article.aid,
            Article.title,
            Article.url
        ).filter(
            Article.date > article.date
        ).filter(func.month(d) == month).filter(
            func.year(d) == year).order_by(Article.date.asc()).first()

        statics = _formatStatics()
        statics['article'] = article
        statics['prev'] = prev_article
        statics['next'] = next_article
        statics['request'] = date

        web.header("Content-Type", "text/html")
        return render.article(statics)


class QueryArticlesByDate:
    """
    以发表日期为准则查询文章，如查询2012年05月发表的所有文章
    """
    def GET(self, date=datetime.datetime.now().strftime("%y-%m"), page=1):
        _dealIp()
        if page is None:
            page = 1
        year, month = map(int, date.split("-"))
        d = Article.__table__.c.date
        per_page = 5
        statics = _formatStatics()
        post_count, statics["articles"] = pageArticles(
            lambda: sql_session.query(Article).filter(
                func.month(d) == month
            ).filter(func.year(d) == year).order_by(
                Article.date.desc()).all(), page, per_page)

        # 所有分类
        statics['all_classes'] = dict(sql_session.query(
            Classes.id, Classes.cls).order_by(Classes.id).all())
        # 文章总数，用于分页
        statics['post_count'] = post_count
        statics['per_page'] = per_page
        statics['request'] = date

        web.header("Content-Type", "text/html")
        return render.home(statics)


class QueryClasses:
    """
    以分类进行文章查询
    """
    def GET(self, cls=''):
        _dealIp()
        articles = sql_session.query(Article).filter(
            Article.classes == cls).order_by(Article.date.desc()).all()
        if articles is None:
            raise web.notfound(render.page404())
        statics = getIpStatics()
        statics['logged'] = session.get('logged', False)
        statics['articles'] = articles
        web.header("Content-Type", "text/html")
        return 'sd'


class QueryType:
    """
    以类型进行文章查询
    """
    def GET(self, type, page):
        _dealIp()
        if page is None:
            page = 1

        t = u"翻译" if type == "translation" else (u"原创" if type == "originality" else u"转载")
        per_page = 5
        statics = _formatStatics()
        post_count, statics["articles"] = pageArticles(
            lambda: sql_session.query(Article).filter(
                Article.type == t
            ).order_by(Article.date.desc()).all(), page, per_page)

        # 所有分类
        statics['all_classes'] = dict(sql_session.query(
            Classes.id, Classes.cls).order_by(Classes.id).all())
        # 文章总数，用于分页
        statics['post_count'] = post_count
        statics['per_page'] = per_page
        statics['request'] = type

        web.header("Content-Type", "text/html")
        return render.home(statics)


class DeleteArticle:
    """
    删除文章
    """
    @needLogin
    def POST(self):
        i = web.input(aid=-1, lol='')
        aid, pwd = i.aid, hashlib.sha1(i.lol).hexdigest()
        if sql_session.query(Lol.lol).filter(Lol.lol == pwd).first() is None:
            msg = u"密码错误"
        else:
            try:
                sql_session.delete(sql_session.query(Article).filter(
                    Article.aid == aid).first())
                msg = "删除成功"
            except UnmappedInstanceError:
                msg = u"文章不存在"
        web.header("Content-Type", "application/json")
        return json.dumps(dict(msg=msg))


class Editor:
    def GET(self):
        """
        返回编辑器页面
        """""
        _dealIp()
        web.header("Content-Type", "text/html")
        return render.editor()


class Backstage:
    """
    后台管理
    """
    @needLogin
    def GET(self):
        web.header("Content-Type", "text/html")
        return render.backstage()

    @needLogin
    def POST(self):
        i = web.input()
        op = i.operation
        if op == "class":  # 分类管理
            cls = dict(sql_session.query(
                Classes.id, Classes.cls).order_by(Classes.id).all())
            web.header("Content-Type", "application/json")
            return json.dumps(cls)
        elif op == 'profile':  # 个人中心
            web.header("Content-Type", "text/html")
            return render.profile()
        elif op == 'comment':  # 评论管理
            web.header("Content-Type", "text/html")
            n = datetime.datetime.now() - datetime.timedelta(930, 0, 0)
            # 只取最近30天内的评论
            comments = sql_session.query(
                Comment.aid,
                Comment.date,
                Comment.author,
                Comment.mail,
                Comment.url,
                Comment.content
            ).filter(
                n < Comment.date
            ).order_by(Comment.date.desc())
            articles = []  # [[title, aid, [comment1, comment2, ……]]]
            titles = []
            for c in comments:
                a = sql_session.query(Article.title, Article.aid).filter(
                    Article.aid == c.aid).first()
                aid = a.aid
                try:
                    # 已经存在这篇文章
                    i = titles.index(aid)
                    articles[i][2].append(c)
                except ValueError:
                    # 不存在这篇文章
                    titles.append(aid)
                    articles.append([a.title, aid, [c]])
            idx = [random.randint(0, 10) for i in range(comments.count())]  # 随机生成11种颜色
            return render.comment(dict(
                articles=articles,
                idx=idx,
                enumerate=enumerate))


class Upload:
    @needLogin
    def POST(self):
        i = web.input()
        ext = i.localUrl.rsplit('.')[-1].lower().replace('jpg', 'jpeg')
        now = str(datetime.datetime.now().strftime('%Y%m%d%H%M%S%f'))
        s = sae.storage.Client()
        img = Image.open(StringIO.StringIO(i.img_data))
        if img.size[0] > 960:  # 最大宽度为960，否则将被裁剪为宽960
            f = StringIO.StringIO()
            resizeImg(img, min_width=960).save(f, ext)
            raw = sae.storage.Object(
                f.getvalue(),
                content_type='image/%s' % ext)
            f.close()
        else:
            raw = sae.storage.Object(i.img_data, content_type='image/%s' % ext)
        url_small = False
        if img.size[0] < 705:
            name = now + '-raw1.%s' % ext  # 只保存原图，无缩放图
        else:
            name = now + '-raw2.%s' % ext  # 有缩放图
            f = StringIO.StringIO()
            resizeImg(img).save(f, ext)
            small = sae.storage.Object(f.getvalue(), content_type='image/%s' % ext)
            url_small = s.put('img', now + '-small.%s' % ext, small)  # 保存缩放图
            f.close()
        url = s.put('img', name, raw)  # 保存原图
        if url_small:
            url = url_small
        web.header("Content-Type", "text/html")
        return '@_@<img src="%s" class="img-from-user"/>$_$' % url


class DeleteClass:
    @needLogin
    def GET(self, id):
        try:
            if id == "1":
                raise IOError
            cls = sql_session.query(Classes).filter(
                Classes.id == int(id)).first()
            sql_session.delete(cls)
            sql_session.commit()
            suc = True
        except Exception:
            suc = False
        web.header("Content-Type", "text/html")
        return suc


class ChangePwd:
    @needLogin
    def POST(self):
        i = web.input(old="", new="", confirm="")
        old, new, confirm = i.old, i.new, i.confirm
        if '' in (old, new, confirm):
            msg = "error"
        return msg


class ThirdApp:
    def GET(self, app):
        if app == '360disk':
            from _3rdapp.CloudDisk360 import main
            main.run()
            return 'ok:)'
        elif app == 'googleping':
            from _3rdapp.GooglePing import main
            return main.run()
        return app


app = web.application(urls, globals())

if web.config.get('_session') is None:
    session = web.session.Session(app, SQLAStore(webpy_table))
    web.config._session = session
else:
    session = web.config._session

app.add_processor(loadSqla)
application = sae.create_wsgi_app(app.wsgifunc())

initDb()
