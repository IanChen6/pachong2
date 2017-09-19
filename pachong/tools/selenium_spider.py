# -*- coding:utf-8 -*-
import os

__author__ = 'IanChen'
#selinium需要专用的driver来调用浏览器

from selenium import webdriver
from scrapy.selector import Selector#对页面提取用selector会比browser自带的元素查找更方便

browser = webdriver.Chrome(executable_path='F:/web_driver_for_chrome/chromedriver.exe')#添加driver的路径
# os.environ["webdriver.chrome.driver"] = "F:/web_driver_for_chrome/chromedriver.exe"

browser.get("http://item.jd.com/5089225.html?from_saf=1&cu=true&utm_source=baidu-search&utm_medium=cpc&utm_campaign=t_262767352_baidusearch&utm_term=13231631448_0_35df3efad1a94b9ab35457129b8e67bf")#调用浏览器模拟登陆京东

print(browser.page_source)#page_source即浏览器打开网页F12之后的html页面

t_selector = Selector(text=browser.page_source)#response的css方法其实就是selector传入了response.text
print(t_selector.css(".J-summary-price .J-p-5089225::text").extract())
browser.quit()#关闭浏览器