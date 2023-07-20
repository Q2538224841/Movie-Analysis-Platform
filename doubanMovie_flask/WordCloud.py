# -*- coding = utf-8 -*-
# @Time : 2023/6/12 2:06
# @Author : 李力
# @File : WordCloud.py
# @Software : PyCharm

import jieba
from matplotlib import pyplot as plt
from wordcloud import WordCloud
from PIL import Image
import numpy as np
import sqlite3

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']

# 准备词云所需的文字（词）
con = sqlite3.connect('../doubanMovie/douban.db')
cur = con.cursor()
sql = "SELECT inq FROM movie250;"
data = cur.execute(sql)
text = ""
for item in data:
    text = text + item[0]
cur.close()
con.close()

# 分词
cut = jieba.cut(text)
words = list(cut)  # 转换为列表形式

# 设置屏蔽词（一般的标点符号）
stopwords = ['。', '的', '，', ' ', '是', '你', '了', '人', '都', '我', '在', '和', '我们', '就是', '最', '不', '让',
             '一个', '被', '与', '一部', '不是', '有', '就', '不会', '没有', '给', '这样', '·', '对', '《', '》', '中',
             '也', '才', '“', '”', '~', '.', '、', '！', '+', '？',
             '…']

# 统计词频
word_counts = {}
for word in words:
    if word not in stopwords:
        if word in word_counts:
            word_counts[word] += 1
        else:
            word_counts[word] = 1

# 打印总词语数
total_words = sum(word_counts.values())
print("总词语数:", total_words)

# 按照出现次数从高到低排序
sorted_word_counts = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)

# 显示每个词语出现的次数
for word, count in sorted_word_counts:
    print(f"{word}: {count}")

# 生成词云
img = Image.open(r'.\static\images\tree.jpg')
img_array = np.array(img)
wc = WordCloud(
    background_color='white',
    mask=img_array,
    font_path="STXINGKA.TTF",
    stopwords=stopwords
)
wc.generate_from_text(' '.join(words))

# 绘制图片
fig = plt.figure(1)
plt.imshow(wc)
plt.axis('off')

plt.show()

# #输出词云图片到文件
# plt.savefig(r'.\static\images\词云.jpg',dpi=1500)
