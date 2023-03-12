"""
本文件用于评估3.2环节的正、逆向最大匹配算法
以召回率、精确率、F值最为评分标准，输出score.txt
"""
import re


def PreProcess(file_path):
    """
        为了处理标准答案中的一些误差，并把标准答案转换成和自己做出的分词一样的格式，方便比较
        :param:file_path:文件地址
        :return:二维列表，每一句*每一个词
        """
    file = open(file_path, 'r', encoding='utf-8')
    try:
        words = file.read()
    finally:
        file.close()
    word_list = []
    lines = words.split('\n')
    for line in lines:
        if line == '':
            continue
        # 单独处理seg&pos文件中的【】nt形式
        temp = re.split('\[|][a-zA-Z]*', line)
        line = ''.join(temp)
        pro_line = re.split('/[a-zA-Z]*[ ]*', line)
        word_list.append(pro_line)
    return word_list


def calculate(standard, myseg):
    """
    精确率就是算正样本中有多少是正确的。公式：P=TP/(TP+FP)
    召回率是所有的正样本中有多少被预测正确了。    公式：R=TP/(TP+FN)
    F1就是综合P,R。   公式：F1=2PR/(R+P)
    :param standard: 二维数组，存储每一行每一个单词
    :param myseg: 二维数组，存储每一行每一个单词
    :return: Precision,Recall,F1
    """
    lines = len(standard)
    if lines != len(myseg):
        print('传入文本处理有误：行数不同')
        return 0, 0, 0
    my_words_num = 0
    standard_words_num = 0
    right_words_num = 0
    for i in range(lines):
        my_line = myseg[i]
        standard_line = standard[i]
        # 计算总词数
        my_words_num += len(my_line)
        standard_words_num += len(standard_line)

        m, s = 0, 0
        lm, ls = len(my_line), len(standard_line)
        while m < lm and s < ls:
            my_word = my_line[m]
            st_word = standard_line[s]
            # 遍历句子中每一个分词
            # 如果直接成功则成功数加一进行下一次匹配
            if my_word == st_word:
                right_words_num += 1
            else:
                # 分词匹配失败
                while True:
                    if len(my_word) < len(st_word):
                        m += 1
                        my_word += my_line[m]
                    elif len(my_word) > len(st_word):
                        s += 1
                        st_word += standard_line[s]
                    elif my_word == st_word:
                        break
            m += 1
            s += 1
        if i > 19000:  # 过大的评判量会导致卡死
            break
    precision = right_words_num / float(my_words_num)  # 精确度计算
    recall = right_words_num / float(standard_words_num)  # 召回率计算
    f = 2 * precision * recall / (precision + recall)  # f值计算
    return precision, recall, f


if __name__ == '__main__':
    LM_Bi_file_path = 'ans/seg_LM.txt'
    LM_Uni_file_path = 'ans/seg_LM_Uni.txt'
    FMM_file_path = 'ans/seg_FMM.txt'
    BMM_file_path = 'ans/seg_BMM.txt'
    seg_file_path = 'DataSet/199801_seg&pos.txt'
    seg = PreProcess(seg_file_path)
    FMM = PreProcess(FMM_file_path)
    BMM = PreProcess(BMM_file_path)
    LM = PreProcess(LM_Uni_file_path)
    LM_Bi = PreProcess(LM_Bi_file_path)
    print('FMM算法的准确率、召回率、f值为：', calculate(seg, FMM))
    print('BMM算法的准确率、召回率、f值为：', calculate(seg, BMM))
    print('LM_Uni算法的准确率、召回率、f值为：', calculate(seg, LM))
    print('LM_Bi算法的准确率、召回率、f值为：', calculate(seg, LM_Bi))
    file = open('ans/score.txt', 'w', encoding='utf-8')  # 输出文件位置
    try:
        file.write('FMM算法的准确率、召回率、f值为：' + str(calculate(seg, FMM)) + '\n')
        file.write('BMM算法的准确率、召回率、f值为：' + str(calculate(seg, BMM)) + '\n')
        file.write('LM_Uni算法的准确率、召回率、f值为：' + str(calculate(seg, LM)) + '\n')
        file.write('LM_Bi算法的准确率、召回率、f值为：' + str(calculate(seg, LM_Bi)) + '\n')
    finally:
        file.close()
