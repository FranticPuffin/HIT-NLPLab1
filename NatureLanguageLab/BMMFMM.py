"""
本文件为机械匹配算法FMM、BMM
"""
import time


def read_dic(dic_path):
    """
    读取文件中的词典，将其转化为机械匹配使用的词典
    :param dic_path: 词典路径
    :return: list形式的词典（由于运行时间过长，可返回set形式的词典），词典中最大词长
    """
    file = open(dic_path, 'r', encoding='utf-8')
    try:
        temp = file.read()
    finally:
        file.close()
    dic1 = temp.split('\n')
    # 定义词典
    dic = []
    m_len = 0
    for words in dic1:
        word = words.split('/')[0]
        # 寻找最长字符串以及拆分词典
        m_len = max(m_len, len(word))
        dic.append(word)
    return set(dic), m_len  # 如果使用正常dic则为list（O（n））耗时较长，如果是set（dic）则是系统自带哈希（O(1))耗时约为3秒


def FMM(aim_path, dic_path, out_path):
    """
    前向最大匹配算法
    :param aim_path:待分词文本地址
    :param dic_path: 词典地址
    :param out_path: 输出地址
    :return: 切分时长
    """
    # 读取待分词文件
    aim_file = open(aim_path, 'r', encoding='utf-8')
    try:
        aim = aim_file.read()
    finally:
        aim_file.close()
    aims = aim.split('\n')
    file = open(out_path, 'w', encoding='utf-8')
    dic, max_len = read_dic(dic_path)
    time_begin = time.time()
    for text in aims:
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
            while tryWord not in dic:
                # 字串长度为1，跳出循环
                if len(tryWord) == 1:
                    break
                # 截掉子串尾部一个字，用剩余部分到字典中匹配
                tryWord = tryWord[:-1]
            # 将匹配成功的词插入到分词列表头部
            segList.append(tryWord)
            # 将匹配成功的词从待分词字符串中去除，继续循环直到分词完成
            text = text[len(tryWord):]
        file.write('/ '.join(segList) + '/ ' + '\n')
    time_end = time.time()
    print('FMM算法运行完成，总耗时：', time_end - time_begin, '(seconds)')
    file.close()
    return time_end - time_begin


def BMM(aim_path, dic_path, out_path):
    """
        后向最大匹配算法
        :param aim_path:待分词文本地址
        :param dic_path: 词典地址
        :param out_path: 输出地址
        :return: 切分时长
        """
    # 读取待分词文件
    aim_file = open(aim_path, 'r', encoding='utf-8')
    try:
        aim = aim_file.read()
    finally:
        aim_file.close()
    aims = aim.split('\n')
    file = open(out_path, 'w', encoding='utf-8')
    dic, max_len = read_dic(dic_path)
    time_begin = time.time()
    for text in aims:
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
            # 逆向取字符串中长度为length的子串
            tryWord = text[len(text) - length:]
            while tryWord not in dic:
                # 字串长度为1，跳出循环
                if len(tryWord) == 1:
                    break
                # 截掉子串头部一个字，用剩余部分到字典中匹配
                tryWord = tryWord[1:]
            # 将匹配成功的词插入到分词列表头部
            segList.insert(1, tryWord)
            # 将匹配成功的词从待分词字符串中去除，继续循环直到分词完成
            text = text[:len(text) - len(tryWord)]
        file.write('/ '.join(segList) + '/ ' + '\n')
    time_end = time.time()
    print('BMM算法运行完成，总耗时：', time_end - time_begin, '(seconds)')
    file.close()
    return time_end - time_begin


if __name__ == '__main__':
    aim_path = 'DataSet/199801_sent.txt'
    dic_path = 'ans/dic.txt'
    FMM(aim_path, dic_path, 'ans/seg_FMM.txt')
    BMM(aim_path, dic_path, 'ans/seg_BMM.txt')
