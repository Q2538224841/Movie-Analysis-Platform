# -*- coding = utf-8 -*-
# @Time : 2023/6/1 9:51
# @Author : 李力
# @File : crawler.py
# @Software : PyCharm

import sqlite3
import re
import urllib.request, urllib.error
from bs4 import BeautifulSoup
import time


def main():
    DBpath = "douban.db"
    initDB(DBpath)
    sourceURL = "https://movie.douban.com/top250?start="
    DataList = getData(sourceURL)  # 爬取网页
    saveData(DataList, DBpath)  # 保存数据


# 爬取网页
def getData(sourceurl):
    # 详情页链接的模式
    MoreurlPattern = re.compile(r'<a href="(.*?)">')  # 创建正则表达式对象，表示规则（字符串的模式）
    # 图片链接的模式
    ImgPattern = re.compile(r'<img alt=.*class="" src="(.*?)"')
    # 作品名的模式
    TitlePattern = re.compile(r'<span class="title">\s*/*\s*(.*?)</span>')  # 可能只有一个作品名，没有别名
    # 相关信息的模式
    InfoPattern = re.compile(r'<p class="">\s*(.*?)\s*</p>', re.S)  # re.S 让换行符\n能被.匹配
    # 评分的模式
    RatingPattern = re.compile(r'<span class="rating_num" property="v:average">(\d\.\d)</span>')
    # 评价人数的模式
    PeoplePattern = re.compile(r'<span>(\d*)人评价</span>')
    # 短评的模式
    InqPattern = re.compile(r'<span class="inq">(.*?)</span>')

    datalist = []

    for i in range(0, 10):  # 调用获取页面信息的函数，10次
        URL = sourceurl + str(i * 25)
        HTML = askURL(URL)  # 保存获取到的网页源码

        # 逐一解析数据
        bs = BeautifulSoup(HTML, "html.parser")
        for item in bs.find_all("div", class_="item"):  # 查找符合要求的字符串，形成列表
            item = str(item)
            data = []  # 保存一部电影的所有信息

            # 详情页链接
            moreurl = re.findall(MoreurlPattern, item)  # re库用来通过正则表达式查找指定的字符串
            data.append(moreurl[0])  # 添加链接

            img = re.findall(ImgPattern, item)
            data.append(img[0])  # 添加图片

            title = re.findall(TitlePattern, item)  # 可能只有一个作品名，没有别名
            data.append(title[0])  # 添加作品名
            if len(title) == 2:
                data.append(title[1])  # 添加别名
            else:
                data.append(' ')  # 别名留空

            info = re.findall(InfoPattern, item)  # 相关信息包括：导演、主演、年份、地区、类型等
            data.append(re.compile(r'^导演:(.*?)\s{2,}').findall(info[0])[0].strip().replace("<br/>", ''))  # 添加导演
            try:
                data.append(re.compile(r'主演:(.*?)<br/>').findall(info[0])[0].strip())  # 部分项由于导演的信息过长导致主演信息被省略
            except IndexError:
                data.append(' ')  # 主演留空
            data.append(re.compile(r'(\d{4}.*?)\s/\s[^/]+\s/\s[^/]+$').findall(info[0])[0])  # 添加年份
            data.append(re.compile(r'/\s([^/]+)\s/\s[^/]+$').findall(info[0])[0])  # 添加地区
            data.append(re.compile(r'/\s([^/]+)$').findall(info[0])[0])  # 添加类型

            rating = re.findall(RatingPattern, item)
            data.append(float(rating[0]))  # 添加评分

            person = re.findall(PeoplePattern, item)
            data.append(int(person[0]))  # 添加评价人数

            inq = re.findall(InqPattern, item)
            if inq:
                data.append(inq[0])  # 添加短评
            else:
                data.append(' ')  # 短评留空

            datalist.append(data)  # 把处理好的一部电影信息放入MovieList

    return datalist


# 得到指定一个URL的网页内容
def askURL(url):
    head = {  # 模拟浏览器头部信息，向豆瓣服务器发送消息
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0; WOW64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 94.0 4606.71 Safari / 537.36 Core / 1.94 .197 .400 QQBrowser / 11.6 .5265 .400"
    }
    # 用户代理，表示告诉豆瓣服务器，我们是什么类型的机器，浏览器（本质上是告诉浏览器，我们可以接收什么水平的文件内容）

    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)

    return html


# 保存数据
def saveData(datalist, dbpath):
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()

    # 将豆瓣上的各项数据存入数据库
    qmark = []
    values = []
    str1 = "INSERT INTO movie250(moreurl, img, title, othertitle, director, cast, year, region, genre, rating, person, inq) VALUES"
    for i in range(len(datalist[0])):
        qmark.append('?')
    str2 = '(' + ','.join(qmark) + ");"
    sql = str1 + str2
    for data in datalist:
        values.append(tuple(data))
    c.executemany(sql, values)

    # 记录数据更新时间
    sql = "UPDATE movie250 SET time = ? WHERE ROWID = 1;"
    jikan = []
    jikan.append(time.strftime("%a %b %d %H:%M:%S %Y", time.localtime()))
    c.execute(sql, tuple(jikan))

    conn.commit()
    c.close()
    conn.close()


def initDB(dbpath):
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()

    sql = "CREATE TABLE movie250(moreurl text, img text, title varchar, othertitle varchar, director text, cast text, year text, region text, genre text, rating numeric, person numeric, inq text, time text);"
    try:
        c.execute(sql)
    except sqlite3.OperationalError:
        c.execute("DROP TABLE movie250")
        c.execute(sql)

    conn.commit()
    c.close()
    conn.close()


if __name__ == "__main__":  # 当程序执行时
    # 调用函数
    main()
    print("爬取完毕!")
