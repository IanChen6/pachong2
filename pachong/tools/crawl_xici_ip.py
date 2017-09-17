

import requests
from scrapy.selector import Selector


def crawl_ips():
    #爬取西刺的免费ip代理
    headers ={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36 QIHU 360SE"}
    re =requests.get("http://www.xicidaili.com/nn/",headers=headers)
    selector= Selector(text=re.text)
    all_trs = selector.css("#ip_list tr")

    for tr in all_trs:
        speed_str = tr.css(".bar::attr(title)").extract()[0]
        if speed_str:
            speed = float(speed_str.split("秒")[0])
