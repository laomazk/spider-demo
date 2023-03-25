import urllib.request
import urllib.parse
import re
import random
from bs4 import BeautifulSoup
import pandas as pd
import time

# 定义第1个分函数joint，用来拼接url
def joint(url,size=None,page=None,type=None,id=None):
    if len(url) > 45:
        condition = 'producttype:' + type + '|status:在售'
        data = {
        'mode': 'statistics',
        'pageSize': size,
        'pageIndex': str(page),
        'conditionStr': condition,
        'start_released': '',
        'end_released': '',
        'orderStr': '1',
        'ascStr': 'ulup'
        }
        joint_str = urllib.parse.urlencode(data)
        url_new = url + joint_str
    else:
        data = {
            'id':id
            }
        joint_str = urllib.parse.urlencode(data)
        url_new = url + joint_str
    return url_new

# 定义第2个函数que_res，用来构建request发送请求，并返回响应response
def que_res(url):

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

    # 构建request的第二步——构建request
    request = urllib.request.Request(url=url, headers=headers)


    # 发起请求的第一步——构建代理池
    proxy_list = [
        {'http':'125.40.29.100:8118'},
        {'http':'14.118.135.10:808'}
        ]
    proxy = random.choice(proxy_list)

    # 发起请求的第二步——创建handler和opener
    handler = urllib.request.ProxyHandler(proxy)
    opener = urllib.request.build_opener(handler)

    # 发起请求的第三步——发起请求，获取响应内容并解码
    response = opener.open(request).read().decode()

    # 返回值
    return response

# 定义第3个函数parse_content_1，用来解析并匹配第一层网页内容，此处使用正则表达式方法
def parse_content_1(response):

    # 写正则进行所需数据的匹配
    re_1 = re.compile(
    r'{"ROWID".*?"ID":"(.*?)","Title":"(.*?)","producttype".*?"issuers":"(.*?)","released":"(.*?) 0:00:00","PeriodTo":(.*?),"StartPrice".*?"moneyinto":"(.*?)","EstimatedRatio1":(.*?),"status":.*?"}')
    contents = re_1.findall(response)
    return contents

# 定义第4个函数parse_content_2，用来解析并匹配第二层网页内容，并输出数据，此处使用BeautifulSoup方法
def parse_content_2(response,content):

    # 使用bs4进行爬取第二层信息
    soup = BeautifulSoup(response)

    # 爬取发行地和收益分配方式，该信息位于id为procon1下的table下的第4个tr里
    tr_3 = soup.select('#procon1 > table > tr')[3]         #select到第四个目标tr
    address = tr_3.select('.pro-textcolor')[0].text        #select到该tr下的class为pro-textcolor的第一个内容（发行地）
    r_style = tr_3.select('.pro-textcolor')[1].text        #select到该tr下的class为pro-textcolor的第二个内容（收益分配方式）

    # 爬取发行规模，该信息位于id为procon1下的table下的第5个tr里
    tr_4 = soup.select('#procon1 > table > tr')[4]         #select到第五个目标tr
    guimo = tr_4.select('.pro-textcolor')[1].text          #select到该tr下的class为pro-textcolor的第二个内容（发行规模：至***万）
    re_2 = re.compile(r'.*?(\d+).*?', re.S)                #设立一个正则表达式，将纯数字提取出来
    scale = re_2.findall(guimo)[0]                         #提取出纯数字的发行规模

    # 爬取收益率，该信息位于id为procon1下的table下的第8个tr里
    tr_7 = soup.select('#procon1 > table > tr')[7]         #select到第八个目标tr
    rate = tr_7.select('.pro-textcolor')[0].text[:(-1)]    #select到该tr下的class为pro-textcolor的第一个内容（且通过下标[-1]将末尾的 % 去除）
    r = rate.split('至')                                   #此处用来提取最低收益和最高收益
    r_min = r[0]
    r_max = r[1]

    # 提取利率等级
    tr_11 = soup.select('#procon1 > table > tr')[11]       #select到第十二个目标tr
    r_grade = tr_11.select('p')[0].text                    #select到该tr下的p下的第一个内容（即利率等级）

    # 保存数据到一个字典中
    item = {
    '产品名称':content[1],
    '发行机构':content[2],
    '发行时间':content[3],
    '产品期限':content[4],
    '投资行业':content[5],
    '首页收益':content[6],
    '发行地': address,
    '收益分配方式': r_style,
    '发行规模': scale,
    '最低收益': r_min,
    '最高收益': r_max,
    '利率等级': r_grade
    }

    # 返回数据
    return item

# 定义一个主函数
def main():


    url_1 = 'http://www.yanglee.com/Action/ProductAJAX.ashx?'
    url_2 = 'http://www.yanglee.com/Product/Detail.aspx?'
    size = input('请输入每页显示数量:')
    start_page = int(input('请输入起始页码:'))
    end_page = int(input('请输入结束页码'))
    type = input('请输入产品类型(1代表信托，2代表资管):')
    items = []                       # 定义一个空列表用来存储数据

    # 写循环爬取每一页
    for page in range(start_page, end_page + 1):

        # 第一层网页的爬取流程
        print('第{}页开始爬取'.format(page))
        # 1、拼接url——可定义一个分函数1：joint
        url_new = joint(url_1,size=size,page=page,type=type)

        # 2、发起请求，获取响应——可定义一个分函数2：que_res
        response = que_res(url_new)

        # 3、解析内容，获取所需数据——可定义一个分函数3：parse_content_1
        contents = parse_content_1(response)

        # 4、休眠2秒
        time.sleep(2)

        # 第二层网页的爬取流程

        for content in contents:
            print('    第{}页{}开始下载'.format(page,content[0]))
            # 1、拼接url
            id = content[0]
            url_2_new = joint(url_2,id=id)      # joint为前面定义的第1个函数

            # 2、发起请求，获取响应
            response_2 = que_res(url_2_new)     # que_res为前面定义的第2个函数

            # 3、解析内容，获取所需数据——可定义一个分函数4：parse_content_2，直接返回字典格式的数据
            item = parse_content_2(response_2,content)

            # 存储数据
            items.append(item)
            print('    第{}页{}结束下载'.format(page,content[0]))
            # 休眠5秒
            time.sleep(5)

        print('第{}页结束爬取'.format(page))


    # 保存数据为dataframe格式CSV文件
    df = pd.DataFrame(items)
    df.to_csv('data.csv',index=False,sep=',',encoding='utf-8-sig')

    print('*'*30)
    print('全部爬取结束')

if __name__ == '__main__':
    # main()
    a = r"[{'ROWID': 21, 'ID': '100000000898359', 'Title': '尚实信远129号集合资金信托计划（第1期）', 'producttype': '信托产品', 'issuers': '天津信托', 'released': '2023/3/16 0:00:00', 'PeriodTo': 12, 'StartPrice': 100, 'moneyinto': '基础产业', 'EstimatedRatio1': 6.8, 'status': '在售', 'NodeCode': '105015016005'}, {'ROWID': 22, 'ID': '100000000825792', 'Title': '丰盈金昇5号集合资产管理计划', 'producttype': '资管产品', 'issuers': '申万宏源', 'released': '2023/3/16 0:00:00', 'PeriodTo': 24, 'StartPrice': 100, 'moneyinto': '金融', 'EstimatedRatio1': 4.1, 'status': '在售', 'NodeCode': '105015016006'}, {'ROWID': 23, 'ID': '100000000826760', 'Title': '丰收信丰6号集合资产管理计划', 'producttype': '资管产品', 'issuers': '中信证券', 'released': '2023/3/16 0:00:00', 'PeriodTo': 14, 'StartPrice': 30, 'moneyinto': '金融', 'EstimatedRatio1': 3.6, 'status': '在售', 'NodeCode': '105015016006'}, {'ROWID': 24, 'ID': '100000000813878', 'Title': '聚鸣多策略9号恒选2期私募证券投资基金（230403）', 'producttype': '私募产品', 'issuers': '聚鸣投资', 'released': '2023/3/16 0:00:00', 'PeriodTo': '', 'StartPrice': 100, 'moneyinto': '金融', 'EstimatedRatio1': '', 'status': '在售', 'NodeCode': '105015016007'}, {'ROWID': 25, 'ID': '100000000837857', 'Title': '一村金衍指数增强3号私募证券投资基金', 'producttype': '私募产品', 'issuers': '一村投资', 'released': '2023/3/16 0:00:00', 'PeriodTo': '', 'StartPrice': 100, 'moneyinto': '金融', 'EstimatedRatio1': '', 'status': '在售', 'NodeCode': '105015016007'}, {'ROWID': 26, 'ID': '100000000853124', 'Title': '勤辰森裕臻享1号私募证券投资基金（230316）', 'producttype': '私募产品', 'issuers': '勤辰私募基金', 'released': '2023/3/16 0:00:00', 'PeriodTo': '', 'StartPrice': 100, 'moneyinto': '金融', 'EstimatedRatio1': '', 'status': '在售', 'NodeCode': '105015016007'}, {'ROWID': 27, 'ID': '100000000865195', 'Title': '凯丰宏观策略11-34号证券投资私募基金（230321）', 'producttype': '私募产品', 'issuers': '凯丰投资', 'released': '2023/3/16 0:00:00', 'PeriodTo': '', 'StartPrice': 100, 'moneyinto': '金融', 'EstimatedRatio1': '', 'status': '在售', 'NodeCode': '105015016007'}, {'ROWID': 28, 'ID': '100000000866963', 'Title': '浑瑾岳阳H3号私募证券投资基金', 'producttype': '私募产品', 'issuers': '浑瑾资本', 'released': '2023/3/16 0:00:00', 'PeriodTo': '', 'StartPrice': 100, 'moneyinto': '金融', 'EstimatedRatio1': '', 'status': '在售', 'NodeCode': '105015016007'}, {'ROWID': 29, 'ID': '100000000813544', 'Title': '楚雄市城乡建设投资集团有限公司债权资产拍卖', 'producttype': '其他产品', 'issuers': 'XX金交所', 'released': '2023/3/16 0:00:00', 'PeriodTo': 12, 'StartPrice': 10, 'moneyinto': '基础产业', 'EstimatedRatio1': 10, 'status': '在售', 'NodeCode': '105015016008'}, {'ROWID': 30, 'ID': '100000000819583', 'Title': '安吉县交通投资发展集团有限公司2023年非公开发行公司债券', 'producttype': '其他产品', 'issuers': '深交所', 'released': '2023/3/16 0:00:00', 'PeriodTo': 60, 'StartPrice': 100, 'moneyinto': '金融', 'EstimatedRatio1': 6, 'status': '在售', 'NodeCode': '105015016008'}]"
    b = parse_content_1(a)
    print(b)