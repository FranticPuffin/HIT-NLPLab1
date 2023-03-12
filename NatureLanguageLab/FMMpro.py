"""
本文件为改进的FMM算法
基本思想为哈希索引，计算单词内每一个字符ascii值模1000加单词长度乘以一千最后模一万
(ans%1000+len(Word)*1000)%10000
"""
import time

from BMMFMM import FMM
from diccut import My_Hash


def parseint(words):
    """
    将字符串形式的数字转化为整形数字
    :param words: 字符串
    :return: 数字
    """
    change = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}
    ans = 0
    for i in words:
        ans = ans * 10 + change[i]
    return ans


def hash_dic(dic_path):
    """
    导入哈希词典（二维数组）
    :param dic_path: dic的地址
    :return: 已经切割好的二维数组，词典中最长单词长度
    """
    dic_file = open(dic_path, 'r', encoding='utf-8')
    try:
        dic = dic_file.read()
    finally:
        dic_file.close()
    first_dic = dic.split('\n')
    hashdic = [[] for _ in range(10000)]  # 定义二维数组
    max_len = 0
    for word in first_dic:
        if word == '':
            continue
        word_info = word.split('\t')
        hashdic[parseint(word_info[2])].append(word_info[0])  # 词典对应索引值加入单词信息
        max_len = max(max_len, len(word_info[0]))
    return hashdic, max_len


def Hash_FMM(data_path, dic_path, out_path):
    """
    基于哈希的机械匹配算法速度优化
    :param data_path: 训练集地址
    :param dic_path: 词典地址
    :param out_path: 输出地址
    :return: 运行时间
    """
    dic, max_len = hash_dic(dic_path)  # 接受词典以及词典中最长长度
    print('字典已初始化完成,词典中最长词长度为：', max_len)
    fr = open(data_path, 'r', encoding='utf-8')
    try:
        data = fr.read()
    finally:
        fr.close()
    sentences = data.split('\n')
    fw = open(out_path, 'w', encoding='utf-8')
    start_time = time.time()
    for text in sentences:
        # 如果句子为空则跳过
        if text == '':
            continue
        # 用于存储切分好词的词表
        segList = [text[:19]]
        text = text[19:]
        while len(text) > 0:
            length = max_len
            # 如果最大分词长度大于待切分字符串长度，则切分长度设置为待切分字符串长度
            if len(text) < max_len:
                length = len(text)
            # 正向取字符串中长度为length的子串
            tryWord = text[:length]
            while tryWord not in dic[My_Hash(tryWord)]:
                # 字串长度为1，跳出循环
                if len(tryWord) == 1:
                    break
                # 截掉子串尾部一个字，用剩余部分到字典中匹配
                tryWord = tryWord[:-1]
            # 将匹配成功的词插入到分词列表尾部
            segList.append(tryWord)
            # 将匹配成功的词从待分词字符串中去除，继续循环直到分词完成
            text = text[len(tryWord):]
        fw.write('/ '.join(segList) + '/ ' + '\n')
    end_time = time.time()
    print('使用了哈希的FMM算法运行时间为{}'.format(end_time - start_time))
    fw.close()
    return end_time - start_time


if __name__ == '__main__':
    dic_path = 'ans/Hash_dic.txt'
    data_path = 'DataSet/199801_sent.txt'
    out_path = 'ans/seg_FMMpro.txt'
    BMM_out_path = 'ans/seg_BMM.txt'
    FMM_out_path = 'ans/seg_FMM.txt'
    Time_path = 'ans/TimeCost.txt'
    Fast_cost = Hash_FMM(data_path, dic_path, out_path)
    FMM_cost = FMM(data_path, dic_path, FMM_out_path)
    file = open(Time_path, 'w', encoding='utf-8')
    try:
        file.write(f'FMM优化前所需时间为：{FMM_cost}（s)，优化后所需时间为{Fast_cost}（s）')
    finally:
        file.close()
