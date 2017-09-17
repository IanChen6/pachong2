

import requests
from scrapy.selector import Selector
import pymysql

cursor=pymysql.connect("","","","")

def crawl_ips():
    #爬取西刺的免费ip代理
    headers ={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36 QIHU 360SE"}
    for i in range(1568):
            re =requests.get("http://www.xicidaili.com/nn/{0}".format(i),headers=headers)#遍历每个页面

    selector= Selector(text=re.text)
    all_trs = selector.css("#ip_list tr")
    ip_list = []

    for tr in all_trs[1:]:#去掉tr的首个空标签
        speed_str = tr.css(".bar::attr(title)").extract()[0]
        if speed_str:
            speed = float(speed_str.split("秒")[0])
        all_texts = tr.css("td::text").extract()
        ip = all_texts[0]
        port = all_texts[1]
        proxy_type = all_texts[5]
        ip_list.append(ip,port,proxy_type,speed)
        print(all_texts)

    for in_info in ip_list:
        cursor.excute(
            """
            insert into proxy_ip(url,url_object_id, title,salary,job_city,work_years,degree_needed,
              job_type, publish_time,job_advantage,job_desc,job_addr,company_name,company_url,tags,crawl_time
              )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE salary=VALUES(salary),job_advantage=VALUES(job_advantage)
        """
        )

class GetIP(object):
    def get_random_ip(self):
        pass

print(crawl_ips())
