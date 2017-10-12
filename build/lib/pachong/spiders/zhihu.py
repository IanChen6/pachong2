# -*- coding: utf-8 -*-
import datetime
import re

from pachong.settings import user_agent_list
import scrapy
import json

from scrapy.loader import ItemLoader
from pachong.items import ZhihuQuestionItem, ZhihuAnswerItem
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from selenium import webdriver
from scrapy.http import HtmlResponse
try:
    import urlparse as parse
except:
    from urllib import parse





class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    #question的第一页answer的请求url
    start_answer_url="https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}"

    # 收集404出错页面
    # handle_httpstatus_list = [404]#设置参数handle_httostatus_list可使404页面不被过滤

    # def __init__(self):
    #     self.fail_urls=[]

    custom_settings = {
        "COOKIES-ENABLED":True
    }#单独改变settings中的参数配置


    agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36"
    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhizhu.com",
        'User-Agent':agent
    }

    # def __init__(self):#在spider中初始化，这样的话，每个spider都有自己的浏览器
    #     self.browser=webdriver.Chrome(executable_path='F:/web_driver_for_chrome/chromedriver.exe')
    #     super(ZhihuSpider,self).__init__()
    #     dispatcher.connect(self.spider_closed,signals.spider_closed)#传递信号。当爬虫关闭处理函数spider_closed
    #signals

    # def spider_closed(self,spider):
    #     print("spider closed")
    #     self.browser.quit()

    def parse(self, response):

        # if response.status==404:
        #     self.fail_urls.append(response.url)#收集404页面的url
        #     self.crawler.status.inc_val('failed_url')#设置404页面的数量为failed_url,inc_val自动加1
        print(response.body)
        #提取HTML页面的所有URL，病跟踪这些URL进一步爬去
    #如果提取到的URL为/question/xxx 就下载之后进入解析函数
        all_urls= response.css("a::attr(href)").extract()
        all_urls=[parse.urljoin(response.url,url) for url in all_urls]

        all_urls = filter(lambda x: True if x.startswith("https") else False, all_urls)
        #filter函数对all_urls进行过滤，（对urls的list进行lambda）如果urls以htpps开头
        for url in all_urls:
            print(url)
            match_obj=re.findall("(.*zhihu.com/question/(\d+))(/|$).*",url)#匹配question的url；由于question的url有两种形式，所以用“或”匹配两种形式
            if match_obj:
                #如果是question页面，则进行解析
                request_url=match_obj[0][0]
                question_id=match_obj[0][1]
                print(request_url,question_id)

                # 生成随机agent
                import random
                random_index = random.randint(0, len(user_agent_list) - 1)
                random_agent = user_agent_list[random_index]
                self.headers["User-Agent"] = random_agent

                yield scrapy.Request(request_url,headers=self.headers,callback=self.parse_question)
                break#打断点使其只发送一个request，调试起来方便
            else:
                pass
                #如果不是question页面，则进一步返回解析url
                # yield scrapy.Request(url, headers=self.headers)



    def parse_question(self,response):
        #处理question页面,从页面提取question item
        #处理新版本的question页面
        if "QuestionHeader-title" in response.text:
            # item_loader = ItemLoader(item=ZhihuQuestionItem(),response=response)
            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            item_loader.add_css("title","h1.QuestionHeader-title::text")#css不能做或关系
            # item_loader.add_xpath("title",'//*[@class=QuestionHeader-title]/h2/a/text()|//*[@class=QuestionHeader-title]/h2/span/text()')

            item_loader.add_css("content", ".QuestionHeader-detail")#取标签下的html
            item_loader.add_value("url",response.url)
            item_loader.add_value("url", response.url)
            match_obj = re.findall("(.*zhihu.com/question/(\d+))(/|$).*",response.url)  # 匹配question的url；由于question的url有两种形式，所以用“或”匹配两种形式
            if match_obj:
                question_id = int(match_obj[0][1])
            item_loader.add_value("zhihu_id", question_id)
            item_loader.add_css("answer_num",".List-headerText span::text")#之后再提取出数字
            item_loader.add_css("comments_num", ".QuestionHeader-Comment button::text")
            item_loader.add_css("watch_user_num", ".NumberBoard-value::text")
            #request返回的关注数和浏览数结构可能相同，所以用数组的方法来找
            item_loader.add_css("topics", ".QuestionHeader-topics .Popover div::text")#返回1个list


            question_item = item_loader.load_item()

        # yield scrapy.Request(self.start_answer_url.format(question_id,20,0),headers=self.headers,callback=self.parse_answer)

        yield question_item#调试answer时将这注释点，避免干扰


    def parse_answer(self,response):
        #处理question的answer
        ans_json = json.loads(response.text)
        is_end=ans_json['paging']['is_end']
        total_answer = ans_json['paging']['totals']
        next_url = ans_json['paging']['next']

        #提取answer元素
        for answer in ans_json["data"]:
            answer_item=ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer['id']
            answer_item["url"] =answer['url']
            answer_item["question_id"] = answer['question']['id']
            answer_item["author_id"] = answer['question']['id'] if "id" in answer["question"] else None
            answer_item["content"] = answer['content'] if "content" in answer else None
            answer_item["praise_num"] = answer['voteup_count']
            answer_item["comments_num"] = answer['comment_count']
            answer_item["crawl_time"] = datetime.datetime.now()
            answer_item["create_time"] = answer['created_time']
            answer_item["update_time"] = answer['updated_time']
            yield answer_item #交给pipeline处理


        if not is_end:
            scrapy.Request(next_url,headers=self.headers,callback=self.parse_answer)



    def start_requests(self):
        return [scrapy.Request("https://www.zhihu.com/#signin", headers=self.headers,callback=self.login)]

    def login(self, response):
        # 获取xsrf
        response.status
        response_text = response.text
        xsrf = re.findall(r'.*?name="_xsrf" value="(.*?)".*', response_text)
        post_url = "https://www.zhihu.com/login/phone_num"
        name=input("input your account")
        pw=input("input your password")
        import time
        t = str(int(time.time() * 1000))  # https://www.zhihu.com/captcha.gif?r=1505053437845&type=login&，获取图片验证码的r参数
        captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login&".format(t)
        if xsrf:
            postdata = {
                '_xsrf': xsrf[1],
                'password': pw,
                'phone_num': name,
                'captcha':""

            }

            yield scrapy.Request(captcha_url,headers=self.headers,meta={"post_data":postdata},callback=self.login_after_captcha)
            # return [scrapy.FormRequest(url=post_url,headers=self.headers,formdata=postdata,callback=self.check_login)]

    def login_after_captcha(self,response):
        with open("captcha.jpg", "wb") as f:
            f.write(response.body)#scrapy中的返回内容在body中
            f.close()
        from PIL import Image
        try:
            im = Image.open("captcha.jpg")
            im.show()
            im.ckose()
        except:
            pass
        captcha = input("input captcha/n")

        postdata=response.meta.get("post_data",{})
        post_url = "https://www.zhihu.com/login/phone_num"
        postdata["captcha"]=captcha

        return [scrapy.FormRequest(url=post_url, headers=self.headers, formdata=postdata, callback=self.check_login)]



    def check_login(self,response):
        #将登录页面返回的结果装换成json格式
        text_json=json.loads(response.text)
        if "msg" in text_json and text_json["msg"]== "登录成功":
            print("已登录")
            for url in self.start_urls:
                yield scrapy.Request(url,dont_filter=True,headers=self.headers)
        else:
            print("登录失败")
            for url in self.start_urls:
                yield scrapy.Request(url,dont_filter=True,headers=self.headers)



