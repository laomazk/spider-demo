import time

import requests
from bs4 import BeautifulSoup
import random
import re
import pandas as pd


# https://www.yanglee.com/Product/Index.aspx
# https://www.yanglee.com/Product/Detail.aspx?id=100000000862268
# http://www.yanglee.com/Action/ProductAJAX.ashx?mode=statistics&pageSize=40&pageIndex=1&ascStr=ulup


def do_req(out_url):
    # 构建request的第一步——构建头部：headers
    # user_agent 放在 http 的请求头中，模拟浏览器做 http 请求，有些 http
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

    return response


def parse_resp(resp, content):
    soup = BeautifulSoup(resp.text, 'html.parser')
    # 爬取发行地和收益分配方式，该信息位于id为procon1下的table下的第4个tr里
    tr_3 = soup.select('#procon1 > table > tr')[3]  # select到第四个目标tr
    address = tr_3.select('.pro-textcolor')[0].text  # select到该tr下的class为pro-textcolor的第一个内容（发行地）
    r_style = tr_3.select('.pro-textcolor')[1].text  # select到该tr下的class为pro-textcolor的第二个内容（收益分配方式）

    # 爬取发行规模，该信息位于id为procon1下的table下的第5个tr里
    tr_4 = soup.select('#procon1 > table > tr')[4]  # select到第五个目标tr
    guimo = tr_4.select('.pro-textcolor')[1].text  # select到该tr下的class为pro-textcolor的第二个内容（发行规模：至***万）
    re_2 = re.compile(r'.*?(\d+).*?', re.S)
    scale = 1
    if (len(re_2.findall(guimo)) > 0):
        scale = len(re_2.findall(guimo)[0])

    # 爬取收益率，该信息位于id为procon1下的table下的第8个tr里
    tr_7 = soup.select('#procon1 > table > tr')[7]  # select到第八个目标tr
    rate = tr_7.select('.pro-textcolor')[0].text[:(-1)]  # select到该tr下的class为pro-textcolor的第一个内容（且通过下标[-1]将末尾的 % 去除）
    r = rate.split('至')  # 此处用来提取最低收益和最高收益
    r_min = r[0]
    r_max = r[1]

    # 提取利率等级
    tr_11 = soup.select('#procon1 > table > tr')[11]  # select到第十二个目标tr
    r_grade = tr_11.select('p')[0].text  # select到该tr下的p下的第一个内容（即利率等级）

    # 保存数据到一个字典中
    item = {
        '产品名称': content['Title'],
        '发行机构': content['issuers'],
        '发行时间': content['released'],
        '产品期限': content['PeriodTo'],
        '投资行业': content['moneyinto'],
        '首页收益': content['EstimatedRatio1'],
        '发行地': address,
        '收益分配方式': r_style,
        '发行规模': scale,
        '最低收益': r_min,
        '最高收益': r_max,
        '利率等级': r_grade
    }

    # 返回数据
    return item


if __name__ == '__main__':
    url_1 = 'http://www.yanglee.com/Action/ProductAJAX.ashx?mode=statistics&pageSize={page_size}&pageIndex={page_index}&ascStr=ulup&conditionStr={con}'
    url_2 = 'http://www.yanglee.com/Product/Detail.aspx?id={id}'

    size = input('请输入每页显示的数量:')
    start_page = int(input('请输入起始页码:'))
    end_page = int(input('请输入结束页码:'))
    product_type = input('请输入产品类型（1代表信托，2代表资管，3代表私募，4代表其他）:')
    items = []

    for page in range(start_page, end_page + 1):
        print('第{}页开始爬取'.format(page))

        # 1. 拼接外层请求链接
        out_url = url_1.format(page_index=page, page_size=size, con=product_type)

        # 2. 发起请求
        list = do_req(out_url).json()['result']
        print(list)

        # 3. 休眠
        time.sleep(2)

        # 第二层网页爬取流程
        for content in list:
            id = content['ID']
            print('第{page}页{id}开始下载'.format(page=page, id=id))
            in_url = url_2.format(id=id)
            resp = do_req(in_url)
            # 解析内容
            item = parse_resp(resp, content)
            print(item)

            # 存储数据
            items.append(item)
            print('第{page}页{id}结束下载'.format(page=page, id=id))
            time.sleep(2)

        print('第{page}页结束爬取'.format(page=page))

    # 保存数据为dataframe格式CSV文件
    df = pd.DataFrame(items)
    # TODO 改成自己要存放的路径和文件名称
    df.to_csv('D:\workspace\spider-demo\data1.csv', index=False, sep=',', encoding='utf-8-sig')

    print('*' * 30)
    print('全部爬取结束')
