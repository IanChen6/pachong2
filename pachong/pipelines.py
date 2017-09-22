# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from twisted.enterprise import adbapi
from scrapy import log


class PachongPipeline(object):
    def process_item(self, item, spider):
        return item

#存储item到数据库(基于twisted框架)
class MysqlTwistedPipline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL_PASSWORD"],
            port=settings["MYSQL_Port"],
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("pymysql", **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        #使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)#返回的query其实是个deffered对象
        query.addErrback(self.handle_error, item, spider) #处理异常

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print (failure)
        # log.err(e)
        pass

    def do_insert(self, cursor, item):
        #执行具体的插入
        #根据不同的item 的cls name构建不同的sql语句并插入到mysql中
        # if item.__class__.name == "ZhihuQuestionItem":#这种方法比较繁杂

        #在items中定义具体的插入数据库的逻辑

        insert_sql, params = item.get_insert_sql()

        cursor.execute(insert_sql, params)

