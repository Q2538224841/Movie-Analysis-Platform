from flask import Flask, render_template, request
import sqlite3
from collections import Counter

app = Flask(__name__)


@app.route('/')
def index():  # put application's code here
    conn, c = connect_database()

    jikan = []
    for item in c.execute("SELECT time FROM movie250 LIMIT 1;"):
        jikan.append(item)

    close_database(conn, c)

    return render_template("index.html", time=jikan[0][0])


@app.route('/home')
def home():
    return index()


@app.route('/list<int:num>')
def lists(num):
    return render_template(f"list{num}.html", movies=lister((str((num - 1) * 50),)))


@app.route('/chart<int:num>')
@app.route('/largechart<int:num>')
def charts(num):
    sql_list = ["SELECT genre FROM movie250 WHERE year >= ? AND year < ?;",
                "SELECT COUNT(*) FROM movie250 WHERE year >= ? AND year < ?;",
                "SELECT genre FROM movie250 WHERE region LIKE ?;", "SELECT COUNT(*) FROM movie250 WHERE region LIKE ?;",
                "SELECT COUNT(*) FROM movie250 WHERE year >= ? AND year < ? AND genre LIKE ?;",
                "SELECT region FROM movie250 WHERE genre LIKE ?;", "SELECT COUNT(*) FROM movie250 WHERE genre LIKE ?;"]

    year_tuple = [(1930, 2030), (1930, 1980), (1980, 2000), (2000, 2030)]
    region_tuple = ['%美国%', '%中国%', '%英国%']
    genre_tuple = ['%剧情%', '%爱情%', '%喜剧%', '%冒险%', '%奇幻%']

    template_name = request.path.replace('/', '') + ".html"

    # 1~4 5~7 8~12 13~17
    if (num > 0 and num < 8) or (num > 12 and num < 18):
        if num < 5:
            x, y, c = counter1(sql_list[0], sql_list[1], year_tuple[num - 1])
        elif num < 8:
            x, y, c = counter1(sql_list[2], sql_list[3], (region_tuple[num - 5],))
        else:
            x, y, c = counter3(sql_list[5], sql_list[6], (genre_tuple[num - 13],))

        return render_template(template_name, xaxis=x, yaxis=y, count=c)

    if num > 7 and num < 13:
        d = counter2(sql_list[4], genre_tuple[num - 8])

        return render_template(template_name, datalist=d)


@app.route('/wordcloud')
def wordcloud():
    return render_template("wordcloud.html")


def connect_database():
    conn = sqlite3.connect("../doubanMovie/douban.db")
    c = conn.cursor()
    return conn, c


def close_database(conn, c):
    c.close()
    conn.close()


def lister(value):
    conn, c = connect_database()

    list = []
    for item in c.execute("SELECT * FROM movie250 LIMIT 50 OFFSET ?;", value):
        list.append(item)

    close_database(conn, c)

    return list


def counter1(sql1, sql2, value):
    conn, c = connect_database()

    movies = [item[0] for item in c.execute(sql1, value)]
    total = next(c.execute(sql2, value))[0]

    close_database(conn, c)

    genre_count = {}  # 创建空字典来存储类型和数量

    for movie in movies:
        genres = movie.split()  # 拆分电影类型为一个列表
        for genre in genres:
            genre_count[genre] = genre_count.get(genre, 0) + 1  # 类型已存在，数量加1；类型不存在，初始化数量为1

    # 将类型及对应的电影数量分别写入列表
    genreList, countList = zip(*genre_count.items())

    return list(genreList), list(countList), total


def counter2(sql, value):
    conn, c = connect_database()

    countList = []
    years = ['1930', '1980', '1990', '2000', '2010', '2030']

    for i in range(1, len(years)):
        count = c.execute(sql,
                          (years[i - 1], years[i], value)).fetchone()[0]
        countList.append(count)

    close_database(conn, c)

    return countList


def counter3(sql1, sql2, value):
    conn, c = connect_database()

    movies = [item[0] for item in c.execute(sql1, value)]
    total = next(c.execute(sql2, value))[0]

    close_database(conn, c)

    genre_count = Counter()

    for movie in movies:
        genres = movie.split()
        genre_count.update(genres)

    # 提取前10个最大值
    top_10_regions, top_10_counts = zip(*genre_count.most_common(10))

    return list(top_10_counts)[::-1], list(top_10_regions)[::-1], total


if __name__ == '__main__':
    app.run()
