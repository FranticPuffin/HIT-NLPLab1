# 实现二元文法
import re
from math import log

from HMM import HMM
from Uni_LM import read_pre_dic, join_DAG


def get_Bi_dic(dic_path):
    """
    生成前缀词典
    :param dic_path:统计词典所在地址
    :return: 生成前缀词典
    """
    pre_dic = {}
    file = open(dic_path, 'r', encoding='utf-8')
    try:
        dic = file.read().split('\n')
    finally:
        file.close()
    for line in dic:
        if line == '':
            continue
        word_fre = line.strip().split('\t')
        word1, word2, freq = word_fre[0], word_fre[1], int(word_fre[2])
        # 前缀词典中不含该词汇，则向前缀词典中加入该词条
        if word1 not in pre_dic:
            pre_dic[word1] = {word2: freq}
        else:
            pre_dic[word1][word2] = freq
    return pre_dic


def generate_equal_class(sentence, prog, replace_char):
    """
    生成等价类算法
    :param sentence: 待切分文本句子
    :param prog: 用来匹配等价类的正则表达式
    :param replace_char: 用单一特殊符号代替
    :return: 改变的句子，句子中被改变的元素集合
    """
    OOV = re.findall(prog, sentence)
    if OOV:
        for word in OOV:
            sentence = sentence.replace(word, replace_char, 1)
    return sentence, OOV


def replace_equal_class(sentence_seg, replace_char, OOV):
    """
    还原等价类算法
    :param sentence_seg: 当前切分词汇集合
    :param replace_char: 之前的替换特殊符号
    :param OOV: 句子中的源成分
    :return: 还原后的句子成分
    """
    j = 0
    for i in range(len(sentence_seg)):
        if sentence_seg[i] == replace_char:
            sentence_seg[i] = OOV[j]
            j += 1
    return sentence_seg


def cal_log(word1, word2, dic, Bi_dic, total):
    """
    计算word1之后是word2的概率的log(平滑算法使用删除插值法）
    :param word1:第一个词
    :param word2:第二个词
    :param dic:一元前缀词典
    :param Bi_dic:二元前缀词典
    :param total:一元词典总词频
    :return:log值的概率形式
    """
    sita = 0.9
    p_word1 = 0.8 * total
    p_word1_p2 = 0.8
    p_word2 = 1
    if word2 in Bi_dic:
        if word1 in Bi_dic[word2]:
            p_word1_p2 += Bi_dic[word2][word1]
    if word1 in dic:
        p_word1 += dic[word1]
    if word2 in dic:
        p_word2 += dic[word2]
    return sita * (log(p_word1_p2) - log(p_word1)) + (1 - sita) * (log(p_word2) - log(total))


def best_way(sentence, dic, Bi_dic, sentence_seg, total_num):
    """
    寻找一个句子的最佳分词方式
    :param sentence:需要分词的句子
    :param dic:一元前缀词典
    :param Bi_dic:二元前缀词典
    :return:返回分词结果
    """
    # 处理百分数
    sentence, OOV1 = generate_equal_class(sentence, '[０-９]*[·．]?[０-９]+[％]', '%')
    # 把年处理成特殊字符‘&’
    sentence, OOV2 = generate_equal_class(sentence, '[０-９]+[年]', '￥')
    # 把月、日处理成特殊字符‘_’
    sentence, OOV3 = generate_equal_class(sentence, '[０-９]+[月日时分]+', '_')
    # 处理未知格式单词
    sentence, OOV4 = generate_equal_class(sentence, '[ａ-ｚＡ-Ｚ－]+[０-９]*[ａ-ｚＡ-Ｚ－]*', '@')
    # 处理剩余数字
    sentence, OOV5 = generate_equal_class(sentence, '[０-９]*[．·]?[０-９]+', '&')
    DAG = join_DAG(sentence, dic)
    route = {}
    n = 5
    length = len(sentence) - 5  # 减掉结尾的<EOS>
    pre_graph = {'<BOS>': {}}  # 记录了当前字为开始对应词的对数概率
    follow_graph = {}  # 记录了当前词节点对应的上一个相连词的图
    for x in DAG[5]:  # 初始化前词是BOS的情况
        pre_graph['<BOS>'][(5, x + 1)] = cal_log("<BOS>", sentence[5:x + 1], dic, Bi_dic, total_num)
    # 对每一个字可能的分词方式生成下一个词的词典
    while n < length:
        i = DAG[n]
        for x in i:
            pre = sentence[n:x + 1]
            current = x + 1
            current_idx = DAG[x + 1]  # 当前位置对应的后续分词
            temp = {}
            for char_i in current_idx:
                word = sentence[current:char_i + 1]
                if word == "<":  # 已经到句尾了
                    temp['<EOS>'] = cal_log(pre, '<EOS>', dic, Bi_dic, total_num)
                else:
                    temp[(current, char_i + 1)] = cal_log(pre, word, dic, Bi_dic, total_num)
            pre_graph[(n, x + 1)] = temp  # 对每一个以n开头的词都建立一个关于下一个词的词典
        n += 1

    words = list(pre_graph.keys())
    for pre in words:
        for word in pre_graph[pre].keys():  # 遍历pre_word的后一个词
            follow_graph[word] = follow_graph.get(word, list())
            follow_graph[word].append(pre)
    words.append('<EOS>')
    # 动态规划
    for word in words:
        if word == '<BOS>':
            route[word] = (0.0, '<BOS>')
        else:
            if word in follow_graph:
                nodes = follow_graph[word]
            else:
                route[word] = (-65507, '<BOS>')
                continue
            route[word] = max((pre_graph[node][word] + route[node][0], node) for node in nodes)

    end = "<EOS>"
    while True:
        end = route[end][1]
        if end == '<BOS>':
            break
        sentence_seg.insert(1, sentence[end[0]:end[1]])
    # 还原日期、数字、字母等
    if len(OOV1) > 0:
        sentence_seg = replace_equal_class(sentence_seg, '%', OOV1)
    if len(OOV2) > 0:
        sentence_seg = replace_equal_class(sentence_seg, '￥', OOV2)
    if len(OOV3) > 0:
        sentence_seg = replace_equal_class(sentence_seg, '_', OOV3)
    if len(OOV4) > 0:
        sentence_seg = replace_equal_class(sentence_seg, '@', OOV4)
    if len(OOV5) > 0:
        sentence_seg = replace_equal_class(sentence_seg, '&', OOV5)
    return sentence_seg


def Bi_seg(Hmm, text_path, dic_path, dic2_path, out_path):
    """
    二元文法分词
    :param text_path:需要分词的文本的地址
    :param dic_path:词典地址
    :param dic_path:二元词典地址
    :return:分词结果
    """
    dic, total_num = read_pre_dic(dic_path)
    Bi_dic = get_Bi_dic(dic2_path)
    file = open(text_path, 'r', encoding='utf-8')
    try:
        text = file.read().split('\n')
    finally:
        file.close()
    file = open(out_path, 'w', encoding='utf-8')
    try:
        for sentence in text:
            if sentence == '':
                continue
            sentence = sentence.strip()
            sentence_seg = []
            # 处理开头的时间信息
            time_prog = '[0-9]{8}-[0-9]{2}-[0-9]{3}-[0-9]{3}'
            times = re.findall(time_prog, sentence)
            if times:
                for time in times:
                    sentence_seg.append(time)
                    sentence = sentence.replace(time, '', 1)
            times = ''
            if len(sentence_seg) != 0:
                times = sentence_seg[0]
            sentence = '<BOS>' + sentence + '<EOS>'
            sentence_seg = best_way(sentence, dic, Bi_dic, sentence_seg, total_num)
            ##未登录词处理
            OOV = []
            if times != '':
                OOV = Hmm.seg_line(sentence_seg[1:], OOV)
            else:
                OOV = Hmm.seg_line(sentence_seg, OOV)
            if times != '':
                OOV.insert(0, times)
            file.write('/ '.join(OOV) + '/ \n')
    finally:
        file.close()


if __name__ == "__main__":
    # 验收时将text改为测试文件即可
    Hmm = HMM('./ans/hmm_pickle.pkl')
    dic_path = './ans/LM_dic.txt'
    dic2_path = './ans/Bi_dic.txt'
    text_path = './dataset/199801_sent.txt'
    out_path = 'ans/seg_LM.txt'
    Bi_seg(Hmm, text_path, dic_path, dic2_path, out_path)
