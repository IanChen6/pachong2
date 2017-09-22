# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from pachong.items import LagouJobItemLoader,LagouJobItem
from pachong.utils.common import get_md5
from datetime import datetime

class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']


    # JOBDIR="job_info/001"

    rules = (
        # https://www.lagou.com/gongsi/j9891.html  follow表示深度解析，即当前页面的所有子页面
        Rule(LinkExtractor(allow=("zhaopin/.*",)),follow=True),
        Rule(LinkExtractor(allow=("gongsi/j\d+.html",)), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True),
    )#不能通过self. 传递parse_job函数,allow实质上是正则表达式，匹配允许的url

    #
    # def parse_start_url(self, response):  # 默认该方法什么都没干
    #     return ['https://www.lagou.com/']

    # def process_results(self, response, results):  # 默认该方法什么都没干
    #     return results

    def parse_job(self, response):
        #解析拉勾网的职位
        item_loader=LagouJobItemLoader(LagouJobItem(),response)
        item_loader.add_css('title','.job-name::attr(title)')
        item_loader.add_value('url',response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_css('salary','.job_request .salary::text')
        item_loader.add_xpath('job_city',"//*[@class='job_request']/p/span[2]/text()")
        item_loader.add_xpath("work_years", "//*[@class='job_request']/p/span[3]/text()")
        item_loader.add_xpath("degree_needed", "//*[@class='job_request']/p/span[3]/text()")
        item_loader.add_xpath("job_type", "//*[@class='job_request']/p/span[3]/text()")
        item_loader.add_css('publish_time',".publish_time::text")
        item_loader.add_css('tags', ".position-label li::text")
        item_loader.add_css("job_advantage", ".job-advantage p::text")
        item_loader.add_css("job_desc", ".job_bt div")
        item_loader.add_css("job_addr", ".work_addr")

        item_loader.add_css("company_url", "#job_company dt a::attr(href)")
        item_loader.add_css("company_name", "#job_company dt a div h2::text")
        
        item_loader.add_value("crawl_time",datetime.now())

        job_item = item_loader.load_item()
        return job_item



