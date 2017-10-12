# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from fake_useragent import UserAgent#开源第三方随机useragent，无需在settings中维护useragentlist
from pachong.tools.crawl_xici_ip import GetIP

class PachongSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

#使用随机USERAGENT的middleware
class RandomUserAgentMiddleware(object):

    def __init__(self,crawler):
        super(RandomUserAgentMiddleware,self).__init__()
        # self.user_agent_list=crawler.settings.get("user_agent_list",[])
        #通过fake-useragent导入随机agent
        self.ua=UserAgent()
        self.ua_type=crawler.settings.get("RANDOM_UA_TYPE","random")


    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)#将crawler传递给RandomU...

    def process_request(self,request,spider):
        # request.headers.setdefault("User-Agent",random())#对user_agent产生随机变量

        def get_ua():
            return getattr(self.ua,self.ua_type)#getattr() 解释为：取ua的属性ua_type
        random_agent=get_ua()
        request.headers.setdefault("User-Agent", get_ua())
        # request.meta["proxy"] = "http://221.202.248.223:8118"   #设置IP代理（西刺免费代理）

class RandomProxyMiddleware(object):
    #动态设置ip代理
    def process_request(self,request,spider):
        get_ip = GetIP()
        request.meta["proxy"] = get_ip.get_random_ip()

from selenium import webdriver
from scrapy.http import HtmlResponse
class JSPageMiddleware(object):
    #通过Chrome请求动态网页

    # def __init__(self):#防止每次访问一个url都重新启动chrome
    #     self.browser=webdriver.Chrome(executable_path='F:/web_driver_for_chrome/chromedriver.exe')
    #     super(JSPageMiddleware,self).__init__()

    def process_request(self, request, spider):
        if spider.name =="zhihu":
            # browser = webdriver.Chrome(executable_path='F:/web_driver_for_chrome/chromedriver.exe')
            # self.browser.get(request.url)
            spider.browser.get(request.url)
            import time
            time.sleep(5)
            print("访问:{0}".format(request.url))

            return HtmlResponse(url=spider.browser.current_url,body=spider.browser.page_source,encoding="utf8",request=request)#直接返回HtmlResponse,就不会再发送到downloader
        #
        # from pyvirtualdisplay import Display
        # display = Display(visible=0,size=(800,600))
        # display.start()#之后正常调用webdriver

        # browser = webdriver.Chrome().......

        #scrapy splash（轻量级加载动态页面）/selenium grid/splinter