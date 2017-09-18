

import requests
from scrapy.selector import Selector
import pymysql

conn=pymysql.connect(host="127.0.0.1",port=3306,user="root",passwd="1029384756",db="zhihu",use_unicode=True,charset="utf8")
cursor=conn.cursor()

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
            insert into proxy_ip(ip,port,proxy_type,speed) VALUES ('{0}', '{1}', '{2}','{3}')
            ip_info[0],ip_info[1],ip_info[2],ip_info[3]
            ON DUPLICATE KEY UPDATE speed=VALUES(speed)
        """
        )
        conn.commit()

class GetIP(object):
    def delete_ip(self,ip):
        #从数据库中删除无效IP
        delete_sql ="""delete from proxy_ip where ip=‘{0}’
        """.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    def judge_ip(self,ip,port):
        #判断ip是否可用
        http_url = "http://www.baidu.com"
        proxy_url = "http://{0}:{1}".format(ip,port)
        try:
            proxy_dict = {
                "http":proxy_url
            }
            response=requests.get(http_url,proxies=proxy_dict)
            return True
        except Exception as e:
            print("invalid ip and port")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >= 200 and code <300:
                print('effected ip')
                return True
            else:
                print("invalid ip and port")
                self.delete_ip(ip)
                return False

    def get_random_ip(self):
        #从数据库中随机获取ip,随机取出1个数据
        random_sql="""
        SELECT ip,port FROM proxy_ip
        ORDER BY RAND()
        LIMIT 1
        """
        result = cursor.execute(random_sql)
        for ip_info in cursor.fetchall():#获取返回值，返回值是个tuple
            ip = ip_info[0]
            port = ip_info[1]

            judge_re = self.judge_ip(ip,port)
            if judge_re:
                return "http://{0}:{1}".format(ip,port)
            else:
                return self.get_random_ip()


if __name__ == "__main__":
    print(crawl_ips())
    GetIP.get_random_ip()
