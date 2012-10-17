# coding: utf-8

from sqlalchemy import Column, func, event, DDL
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import TINYTEXT, CHAR, VARCHAR, TEXT, TIMESTAMP, INTEGER, ENUM, TINYINT, BOOLEAN

from settings import mysql_engine, sessionmaker

Base = declarative_base()

class Lol(Base):
    __tablename__ = 'lol'
    lol = Column(CHAR(40), primary_key=True)
    def __init__(self, lol):
        self.lol = lol

class WebpySession(Base):
    __tablename__ = 'sessions'
    session_id = Column(CHAR(128), primary_key=True)
    atime = Column(TIMESTAMP, nullable=False, default=func.current_timestamp())
    data = Column(TEXT, nullable=True)
webpy_table = WebpySession.__table__

class Ip(Base):
    __tablename__ = 'ip'
    ip = Column(CHAR(15), primary_key=True)
    visit = Column(INTEGER, nullable=False)
    position = Column(VARCHAR(50), nullable=False)
    time = Column(TIMESTAMP, nullable=False, default=func.current_timestamp())
    def __init__(self, ip, visit, position):
        self.position = position
        self.visit = visit
        self.ip = ip

class Article(Base):
    __tablename__ = 'article'
    aid = Column(INTEGER(unsigned=True, zerofill=True), autoincrement=True, primary_key=True)
    title = Column(TINYTEXT, nullable=False) # 最多85个字
    content = Column(TEXT, nullable=False) # 最多21845个字
    classes = Column(TEXT, nullable=False) # 最多10个字 | 自定义的分类
    type = Column(ENUM(u"原创", u"转载", u"翻译"), nullable=False, default=u"原创")
    pv = Column(INTEGER(unsigned=True), default=0, nullable=False) # 浏览数
    pwd = Column(BOOLEAN, default=False, nullable=False) # 访问是否要密码
    reviewable = Column(BOOLEAN, default=True, nullable=False) # 可否评论
    reproduced = Column(BOOLEAN, default=True, nullable=False) # 可否转载
    # 自动填充字段
    date = Column(TIMESTAMP)
    # 可选项
    tags = Column(TINYTEXT) # 最多85个字
    origin = Column(VARCHAR(1000)) # 转载自
    announcement = Column(TEXT) # 转载声明
    url = Column(VARCHAR(1000)) # 文章的英文网址

class Comment(Base):
    __tablename__ = 'comment'
    cid = Column(INTEGER(unsigned=True, zerofill=True), primary_key=True) # 此评论id
    aid = Column(INTEGER(unsigned=True, zerofill=True), nullable=False) # 文章id
    pid = Column(INTEGER(unsigned=True, zerofill=True)) # 父级评论的id，如果为空，则等于aid，即此评论是顶级评论
    date = Column(TIMESTAMP, default=func.current_timestamp(), nullable=False)
    author = Column(VARCHAR(32))
    content = Column(TEXT, nullable=False)
    mail = Column(VARCHAR(50))
    url = Column(VARCHAR(175)) # 评论者网址

class Classes(Base):
    __tablename__ = 'classes'
    id = Column(INTEGER(unsigned=True), primary_key=True)
    cls = Column(VARCHAR(15), nullable=False, unique=True) # 最多15个字 | 自定义的分类

metadata = Base.metadata

event.listen(
    Article.__table__,
    "after_create",
    DDL("ALTER TABLE %(table)s AUTO_INCREMENT = 100001;")
) # 使得aid字段的自增初始值为100001, MySQL没有Sequence所以不能用Sequence来操作

event.listen(
    Comment.__table__,
    "after_create",
    DDL("ALTER TABLE %(table)s AUTO_INCREMENT = 100001;")
)

def initDb():
    metadata.create_all(mysql_engine)
    session = sessionmaker(bind=mysql_engine)()
    # 初始化
    session.add(Classes(cls=u"默认分类"))
    try:
        session.commit()
    except IntegrityError: # 已经初始化过了
        pass

if __name__ =='__main__':
    initDb()

