# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
from datetime import datetime

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose

from pachong.settings import SQL_DATE_FORMAT,SQL_DATETIME_FORMAT
from pachong.utils.common import extract_num

from w3lib.html import remove_tags

class PachongItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def remove_splash(value):
    #去掉工作城市的斜线
    return value.replace("/","")

# def remove_html_tags(value):
#     #去掉html的tag
#     return
def handle_jobaddr(value):
    addr_list=value.split("\n")
    addr_list=[item.strip() for item in addr_list if item.strip() !="查看地图"]
    return "".join(addr_list)

class ZhihuQuestionItem(scrapy.Item):
    #知乎的问题Item
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()
    # crawl_update_time = scrapy.Field()
    # create_time = scrapy.Field()
    # update_time = scrapy.Field() 在question页面获取不到

    def get_insert_sql(self):
        # 插入知乎question表的sql语句
        #处理主键重复
        insert_sql = """
            insert into question(zhihu_id, topics, url, title, content, answer_num, comments_num,
              watch_user_num, click_num, crawl_time
              )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num), comments_num=VALUES(comments_num),
              watch_user_num=VALUES(watch_user_num), click_num=VALUES(click_num)
        """
        zhihu_id = self["zhihu_id"][0]
        topics = ",".join(self["topics"])
        url = self["url"][0]
        title = "".join(self["title"])
        content = "".join(self["content"])
        answer_num = extract_num("".join(self["answer_num"]))
        comments_num = extract_num("".join(self["comments_num"]))

        if len(self["watch_user_num"]) == 2:
            watch_user_num = int(self["watch_user_num"][0])
            click_num = int(self["watch_user_num"][1])
        else:
            watch_user_num = int(self["watch_user_num"][0])
            click_num = 0

        crawl_time = datetime.now().strftime(SQL_DATETIME_FORMAT)

        params = (zhihu_id, topics, url, title, content, answer_num, comments_num,
                  watch_user_num, click_num, crawl_time)#顺序与上述insert语句中的顺序

        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    #知乎的答案Item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    crawl_time = scrapy.Field()
    # crawl_update_time = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()

    def get_insert_sql(self):
        # 插入知乎answer表的sql语句
        insert_sql = """
            insert into answer(zhihu_id, topics, url, title, content, answer_num, comments_num,
              watch_user_num, click_num, crawl_time
              )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num), comments_num=VALUES(comments_num),
              watch_user_num=VALUES(watch_user_num), click_num=VALUES(click_num)
        """

        create_time = datetime.fromtimestamp(self["create_time"]).strftime(SQL_DATETIME_FORMAT)#将int类型转换成datetime类型
        update_time = datetime.fromtimestamp(self["update_time"]).strftime(SQL_DATETIME_FORMAT)
        zhihu_id = self["zhihu_id"][0]
        #或者zhihu_id = "".join(self["zhihu_id"]）
        topics = ",".join(self["topics"])
        url = self["url"][0]
        title = "".join(self["title"])
        content = "".join(self["content"])
        answer_num = extract_num("".join(self["answer_num"]))
        comments_num = extract_num("".join(self["comments_num"]))

        if len(self["watch_user_num"]) == 2:
            watch_user_num = int(self["watch_user_num"][0])
            click_num = int(self["watch_user_num"][1])
        else:
            watch_user_num = int(self["watch_user_num"][0])
            click_num = 0

        crawl_time = datetime.now().strftime(SQL_DATETIME_FORMAT)#将time转换成string类型

        params = (zhihu_id, topics, url, title, content, answer_num, comments_num,
                  watch_user_num, click_num, crawl_time)

        return insert_sql, params

class LagouJobItemLoader(ItemLoader):
    #自定义itemloader
    default_output_processor = TakeFirst()


class LagouJobItem(scrapy.Item):
    #拉钩网职位信息
    url = scrapy.Field()
    url_object_id= scrapy.Field()
    title= scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    work_years = scrapy.Field(
       input_processor= MapCompose(remove_splash)
    )
    degree_needed  = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field(
        input_processor=MapCompose(remove_tags)#移除html的tags
    )
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags,handle_jobaddr)  # 移除html的tags
    )
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    tags = scrapy.Field(
        input_processor= Join(",")
    )
    crawl_time = scrapy.Field()
    def get_insert_sql(self):
        # 插入LAGOUJOB表的sql语句
        insert_sql = """
            insert into lagou_job(url,url_object_id, title,salary,job_city,work_years,degree_needed,
              job_type, publish_time,job_advantage,job_desc,job_addr,company_name,company_url,tags,crawl_time
              )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE salary=VALUES(salary),job_advantage=VALUES(job_advantage)
        """
        params = (self["url"],self["url_object_id"], self["title"],self["salary"],self["job_city"],self["work_years"],self["degree_needed"],
                  self["job_type"], self["publish_time"],self["job_advantage"],self["job_desc"],self["job_addr"],self["company_name"],self["company_url"],self["tags"],self["crawl_time"].strftime(SQL_DATETIME_FORMAT))
        return insert_sql,params