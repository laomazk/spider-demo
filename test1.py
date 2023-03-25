import json

import requests
from bs4 import BeautifulSoup
import random
import re
import urllib.request
import urllib.parse


def do_req(out_url):
    # 构建request的第一步——构建头部：headers
    USER_AGENTS = [
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    ]
    user_agent = random.choice(USER_AGENTS)
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'www.yanglee.com',
        'Referer': 'http://www.yanglee.com/Product/Index.aspx',
        'User-Agent': user_agent,
        'X-Requested-With': 'XMLHttpRequest'
    }
    response = requests.get(url=out_url, headers=headers, verify=False)
    print(str(response.json()['result']))
    pass

# 定义第3个函数parse_content_1，用来解析并匹配第一层网页内容，此处使用正则表达式方法
def parse_content_1(response):

    # 写正则进行所需数据的匹配
    re_1 = re.compile(
    r'{"ROWID".*?"ID":"(.*?)","Title":"(.*?)","producttype".*?"issuers":"(.*?)","released":"(.*?) 0:00:00","PeriodTo":(.*?),"StartPrice".*?"moneyinto":"(.*?)","EstimatedRatio1":(.*?),"status":.*?"}')
    contents = re_1.findall(response)
    return contents


if __name__ == '__main__':
    do_req(
        'https://www.yanglee.com/Action/ProductAJAX.ashx?mode=statistics&pageSize=1&pageIndex=1&ascStr=ulup&conditionStr=1')
