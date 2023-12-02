# -*- coding = utf-8 -*-
# @Time : 2023/6/1 10:04
# @File : testSQLite.py
# @Software : PyCharm

import sqlite3
from collections import Counter


def main():
    genre_tuple = ['%剧情%', '%爱情%', '%喜剧%', '%冒险%', '%奇幻%']
    datalist = [['类型', '剧情', '爱情', '喜剧', '冒险', '奇幻']]

    print([('%' + genre + '%',) for genre in datalist[0][1:]][12 - 9])
    print((genre_tuple[12 - 9],))


def counter(sql1, sql2, value):
    conn = sqlite3.connect("../douban.db")
    c = conn.cursor()

    movies = [item[0] for item in c.execute(sql1, value)]
    total = next(c.execute(sql2, value))[0]

    c.close()
    conn.close()

    genre_count = {}  # 创建空字典来存储类型和数量

    for movie in movies:
        genres = movie.split()  # 拆分电影类型为一个列表
        for genre in genres:
            genre_count[genre] = genre_count.get(genre, 0) + 1  # 类型已存在，数量加1；类型不存在，初始化数量为1

    # 将类型及对应的电影数量分别写入列表
    genreList, countList = zip(*genre_count.items())

    return list(genreList), list(countList), total


def top10(sql1, sql2, value):
    conn = sqlite3.connect("../douban.db")
    c = conn.cursor()

    movies = [item[0] for item in c.execute(sql1, value)]
    total = next(c.execute(sql2, value))[0]

    c.close()
    conn.close()

    genre_count = Counter()

    for movie in movies:
        genres = movie.split()
        genre_count.update(genres)

    # 提取前10个最大值
    top_10_regions, top_10_counts = zip(*genre_count.most_common(10))

    return list(top_10_regions), list(top_10_counts), total


if __name__ == "__main__":  # 当程序执行时
    # 调用函数
    main()
