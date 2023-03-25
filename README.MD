# SPIDER-DEMO

## 1 什么是爬虫

### 1.1 请求网页内容

爬虫就是使用代码对指定的网页发出请求，获取网页的内容。这个过程本质上跟我们平时浏览网页是一样的，只是我们平时浏览网页，浏览器会多出一个渲染页面的步骤。

### 1.2 解析网页内容

就是将我们代码请求网页获得的原始数据进行提取，获取我们想要的内容

### 1.3 储存和分析数据

可以将数据存储进数据库，或用一些特定的库比如 pandas 做数据分析，具体需求具体分析

> 注意点：
> 
> 1. 不爬敏感数据
> 
> 2. 不做高频率请求

## 2 什么是 HTTP

Hypertext Transfer Protocol 超文本传输协议。举个例子，浏览器是客户端，某网站的服务器是相应端，HTTP 就是一种客户端和服务器之间的请求响应协议。

### 2.1 请求方法

1. GET：获得数据（查询）

2. POST：创建数据（修改、删除、新增）

3. ...

### 2.2 请求示例

三部分组成：请求行、请求头、请求体

```bash
## 请求行
POST /user/info HTTP/1.1
## 请求头
HOST: www.xxx.com
User-Agent:curl/7.77.0
Accept:*/*

## 请求体
{"username":"mzk","password":"xxx"}

```

- User-Agent：用来告知服务器客户端的相关信息，让服务器判断请求是通过什么客户端发出来的，比如是不是浏览器

## 3 Requests 库

是 Python 一个比较常用的 HTTP 请求库，我们通过他编写代码对服务器发起 HTTP 请求

### 3.1 安装

```bash
pip install requests
```

### 3.2 示例

```py
import requests
response = requests.get(url=out_url, headers=headers, verify=False)
```

### 3.3 Headers 请求头

请求头会附带一些我们向服务器发起请求时候的信息，默认是会带上一些常用的，有的网站会有一定的反爬虫机制，这时候我们要指定一些请求的数据信息，就要用到 headers 参数

headers 是一个字典型的数据结构，一般来说就是一个 k-v 接口

```py
{"name":"mazikai","age":18}
```



## 4 Beautiful Soup

Python 比较常用的用来解析网页数据的库。

### 4.1 安装

```bash
pip install bs4
```

### 4.2 示例

```py
from bs4 import BeautifulSoup
soup = BeautifulSoup(resp.text, 'html.parser')
# 爬取发行地和收益分配方式，该信息位于id为procon1下的table下的第4个tr里
tr_3 = soup.select('#procon1 > table > tr')[3]  # select到第四个目标tr
```
