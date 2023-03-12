# -*- coding: utf-8 -*-
"""
本文件为切分词典文件，包含直接切分词典，计算哈希值，生成哈希词典，生成基于统计的词典
"""
import re


# 待分词典文件
def diccut(dic_path, DataSet_path):
    """
    最简单的词典切分：读取数据集，去除数据集中的空格和诸如【东方明珠\n】nt的【】形式
    :param dic_path:词典地址
    :param DataSet_path:数据集地址
    :return:空（将输出写入文件）
    """
    file = open(DataSet_path, 'r', encoding='utf-8')
    try:
        words = file.read()
    finally:
        file.close()
    file1 = open(dic_path, 'w', encoding='utf-8')
    dates, punc = words, words
    # 提取词汇/词性以及标点的正则表达式
    match = re.findall('[０-９]*[\u4e00-\u9fa5]*[·\.]?[０-９]*/[a-zA-Z]+', words)
    words = '\n'.join(set(match))
    match_punc = re.findall('.?/w', punc)
    punc = '\n'.join(set(match_punc))
    try:
        file1.write(words + '\n' + punc)
    finally:
        file1.close()
        # 单独处理形如19980131-02-008-006/m的日期
        file2 = open('ans/date.txt', 'w', encoding='utf-8')
        match_date = re.findall('[0-9]{8}-[0-9]{2}-[0-9]{3}-[0-9]{3}/m', dates)
        dates = '\n'.join(match_date)
        try:
            file2.write(dates)
        finally:
            file2.close()


def My_Hash(Word):
    """
    索引结构，将词转化为哈希值,原理为先找到单字的哈希值，再拼接到一起
    :param Word: 单词
    :return: 单词对应的哈希值
    """
    ans = 0
    change = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'a': 10, 'b': 11, 'c': 12,
              'd': 13, 'e': 14, 'f': 15}
    for w in Word:
        w_hash = 0
        new = ascii(w)[3:-1]
        for n in new:
            w_hash = change[n] + w_hash * 16
        ans += w_hash
    return (ans % 1000 + len(Word) * 1000) % 10000  # 计算单词内每一个字符ascii值模1000加单词长度乘以一千最后模一万即可构造哈希词典


def Hashdic(data_path, dic_path):
    """
    将词典哈希化：输入原词典，输出切分词典
    :param dic_path:
    :return:
    """
    file = open(data_path, 'r', encoding='utf-8')
    try:
        words = file.read()
    finally:
        file.close()
    dics = words.split('\n')
    fin = []
    for word in dics:
        Word_Info = word.split('/')
        Word_Info.append(str(My_Hash(Word_Info[0])))
        fin.append(Word_Info)
    fin.sort(key=lambda x: len(x[0]), reverse=True)
    file = open(dic_path, 'w', encoding='utf-8')
    for word in fin:
        file.write(word[0] + '\t' + word[1] + '\t' + word[2] + '\n')
    file.close()


def LMdic(data_path, dic_path):
    """
    生成基于词频统计的词典
    :param data_path:输入数据集的path
    :return: 词典
    """
    dic = {}
    file = open(data_path, 'r', encoding='utf-8')
    try:
        texts = file.read()
    finally:
        file.close()
    lines = texts.split('\n')
    for line in lines:
        # 去空行
        if line == '':
            continue
        # 将每句分词,句首去掉时间
        words = line.split(' ')[1:]
        for word in words:
            if word == ' ':
                continue
            # 将词汇设置为元组，方便当完全一致时统计次数
            word_tag = tuple(word.strip().split('/'))
            # 遇到空缺，跳过
            if len(word_tag[0]) == 0 or len(word_tag[1]) == 0:
                continue
            # 去除一部分前面有[的词
            if word_tag[0][0] == '[':
                word_tag = (word_tag[0][1:], word_tag[1])
            # 去除词性中有]的词
            if ']' in word_tag[1]:
                word_tag = (word_tag[0], word_tag[1].split(']')[0])
            if word_tag in dic.keys():
                dic[word_tag] += 1
            else:
                dic[word_tag] = 1
    dic = sorted(dic.items(), key=lambda e: e[1], reverse=False)
    file = open(dic_path, 'w', encoding='utf-8')
    for word in dic:
        file.write(word[0][0] + '\t' + word[0][1] + '\t' + str(word[1]) + '\n')
    file.close()
    return dic


def Bidic(data_path, dic_path):
    """
        生成二元文法的词典
        :param data_path:输入数据集的path dic_path:输出词典的path
        :return: 词典
        """
    dic = {}
    file = open(data_path, 'r', encoding='utf-8')
    try:
        texts = file.read()
    finally:
        file.close()
    lines = texts.split('\n')
    for line in lines:
        temp_list = []
        # 去空行
        if line == '':
            continue
        # 将每句分词,句首去掉时间
        words = line.split(' ')[1:]
        for word in words:
            if word == ' ':
                continue
            # 将词汇设置为元组，方便当完全一致时统计次数
            word_tag = tuple(word.strip().split('/'))
            # 遇到空缺，跳过
            if len(word_tag[0]) == 0 or len(word_tag[1]) == 0:
                continue
            # 去除一部分前面有[的词
            if word_tag[0][0] == '[':
                word_tag = (word_tag[0][1:], word_tag[1])
            temp_list.append(word_tag[0])
        # 加入句首和句尾标志
        temp_list.append("<EOS>")
        temp_list.insert(0, '<BOS>')
        for j in range(len(temp_list) - 1):
            pair = (temp_list[j], temp_list[j + 1])
            if pair in dic:
                dic[pair] += 1
            else:
                dic[pair] = 1
    dic = sorted(dic.items(), key=lambda e: e[1], reverse=False)
    file = open(dic_path, 'w', encoding='utf-8')
    for word in dic:
        file.write(word[0][0] + '\t' + word[0][1] + '\t' + str(word[1]) + '\n')
    file.close()
    return dic


if __name__ == '__main__':
    DataSet_path = 'DataSet/199801_seg&pos.txt'
    dic_path = 'ans/dic.txt'
    Hash_dic_path = 'ans/hash_dic.txt'
    LM_dic_path = 'ans/LM_dic.txt'
    LM_Data_path = 'DataSet/199801_seg&pos.txt'
    Bi_dic_path = 'ans/Bi_dic.txt'

    diccut(dic_path, DataSet_path)  # 单独生成普通词典
    Hashdic(dic_path, Hash_dic_path)  # 生成带有哈希值的词典
    LMdic(LM_Data_path, LM_dic_path)  # 生成基于统计的词典
    Bidic(LM_Data_path, Bi_dic_path)  # 生成适合二元文法的词典
