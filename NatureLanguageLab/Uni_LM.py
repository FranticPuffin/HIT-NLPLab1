"""
实现一元文法分词
"""
from math import log  # 计算概率时需要使用log相加，否则小数相乘数值过低精度不够


def read_pre_dic(dic_path):
    """
    读取基于统计词频的词典（LM_dic）
    :param dic_path: 词典路径
    :return: 词频词典，总词数
    """
    total_nums = 0  # 总词数
    pre_dic = {}  # 前缀词典
    file = open(dic_path, 'r', encoding='utf-8')
    try:
        dic = file.read().split('\n')
    finally:
        file.close()
    for word_tag in dic:
        if word_tag == '':
            continue
        word_tags = word_tag.strip().split('\t')
        word = word_tags[0]
        for i in range(len(word)):  # 创建前缀词典
            if word[:i + 1] not in pre_dic:
                pre_dic[word[:i + 1]] = 0
        word_times = int(word_tags[2])  # 根据词典，词汇信息分别是词[0] 词性[1] 词频[2]
        if word not in pre_dic.keys():  # 如果该词是第一次出现
            pre_dic[word] = word_times
        else:
            pre_dic[word] += word_times  # 该词是某词的前缀如果或该词因为不同词性被区分则在一元文法中混为一起
        total_nums += word_times  # 总词频等于单词频之和
    print(f'词典中总词频为{total_nums}')
    return pre_dic, total_nums


def join_DAG(text, dic):
    """
        利用前缀词典，将待分词句子切割成有向无环图
        :param text: 待切分句子
        :param dic: 前缀词典
        :return: dict:字典存储该句子生成的有向无环图
    """
    text_len = len(text)
    DAG = {}
    for i, word in enumerate(text):
        temp = []  # 存储当前字开头的路径
        cur = word
        j = i
        while j < text_len:
            if cur in dic.keys() and dic[cur] > 0:
                temp.append(j)  # 将存在成为词概率的字组存入temp
            j += 1
            cur = text[i:j + 1]
        if not temp:
            temp.append(i)
        DAG[i] = temp  # 将第i个字的转移概率存入有向无环图
    return DAG


def Uni_seg(text_path, dic_path, ans_path):
    """
    一元分词文法
    :param text_path: 待切分文本地址
    :param dic_path: 基于统计的一元词典地址
    :param ans_path: 结果路径
    :return: Null（直接将结果写进ans_path）
    """
    dic, total_num = read_pre_dic(dic_path)
    total_log = log(total_num)
    file = open(text_path, 'r', encoding='utf-8')
    try:
        text = file.read().split('\n')
    finally:
        file.close()
    file = open(ans_path, 'w', encoding='utf-8')
    try:
        for words in text:
            way = {}
            # 去空行
            if words == '':
                continue
            words = words.strip()
            sentence_seg = []
            # 处理开头的时间信息
            sentence_seg.append(words[:19])
            words = words[19:]
            DAG = join_DAG(words, dic)
            w_len = len(words)
            way[w_len] = (0, 0)
            for i in range(w_len - 1, -1, -1):
                way[i] = max((log(dic.get(words[i:j + 1]) or 1) - total_log + way[j + 1][0], j) for j in DAG[i])
            sen_len = len(words)
            i = 0
            while i < sen_len:
                sentence_seg.append(words[i:way[i][1] + 1])
                i = (way[i][1] + 1)
            file.write('/ '.join(sentence_seg) + '/\n')
    finally:
        file.close()


if __name__ == "__main__":
    data_set = './DataSet/199801_sent.txt'
    dic_path = './ans/LM_dic.txt'
    ans_path = 'ans/seg_LM_Uni.txt'
    Uni_seg(data_set, dic_path, ans_path)
