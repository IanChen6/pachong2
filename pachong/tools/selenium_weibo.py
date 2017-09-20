# -*- coding:utf-8 -*-
__author__ = 'IanChen'

from selenium import webdriver
from scrapy.selector import Selector#对页面提取用selector会比browser自带的元素查找更方便

browser = webdriver.Chrome(executable_path='F:/web_driver_for_chrome/chromedriver.exe')#添加driver的路径


browser.get("https://weibo.com/")#调用浏览器模拟登陆知乎
import time
time.sleep(10)
browser.find_element_by_css_selector("#loginname").send_keys('626614767@qq.com')
browser.find_element_by_css_selector(".W_login_form input[type='password']").send_keys('welcome1993219')#send_keys：实现往框中输入内容

browser.find_element_by_css_selector(".W_login_form a[node-type='submitBtn']").click()

browser.execute_script("window.scrollTo(0,document.body.scrollHeight); var lenOfPage=document.body.scrollHeight;return lenOfPage")