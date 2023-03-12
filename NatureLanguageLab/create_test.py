"""
本文件用于切分处理数据集，以达到测试未登录词识别的目的
"""
import random

from diccut import LMdic, Bidic

P_test = 0.5  # 切分成测试集的概率


def change(sentence):
    """
    将带标注的句子切分成不带标注的句子
    :param sentence: 带标注的句子
    :return: 不带标注的句子
    """
    words = sentence.split(' ')
    ans = ''
    for word in words:
        if word == '':
            continue
        word = word.split('/')[0]
        if word[0] == '[':
            ans += word[1:]
        else:
            ans += word
    return ans


def cut_set(text_path1, text_path2, text_path3):
    """
    函数功能：将带标注的文件更改为不带标注的文件
    :param text_path: 源文件
    :return: 新测试文件,测试文件的标注文件,训练集
    """
    file = open(text_path1, 'r', encoding='utf-8')
    try:
        text = file.read().split('\n')
    finally:
        file.close()

    file = open(text_path2, 'r', encoding='utf-8')
    try:
        text += file.read().split('\n')
    finally:
        file.close()

    file = open(text_path3, 'r', encoding='utf-8')
    try:
        text += file.read().split('\n')
    finally:
        file.close()
    train_set = []
    test_set = []
    ans_set = []
    for sentence in text:
        if text == '':
            continue
        if random.random() < P_test:
            ans_set.append(sentence)
            test_set.append(change(sentence))
        else:
            train_set.append(sentence)

    return test_set, train_set, ans_set


def write_sentence(aim_path, aim_text):
    """
    将目的文本写入目的文件中
    :param aim_path: 目的文件地址
    :param aim_text: 目的文件
    :return:
    """
    file = open(aim_path, 'w', encoding='utf-8')
    try:
        for sentence in aim_text:
            if sentence == '':
                continue
            file.write(sentence + '\n')
    finally:
        file.close()


if __name__ == '__main__':
    text_path1 = 'DataSet/199801_seg&pos.txt'
    text_path2 = 'DataSet/199802.txt'
    text_path3 = 'DataSet/199803.txt'
    ans_path = 'test/199801_03_ans.txt'
    train_path = 'test/199801_03_train.txt'
    test_path = 'test/199801_03_test.txt'
    test, train, ans = cut_set(text_path1, text_path2, text_path3)
    Bi_dic = 'test/Bidic.txt'
    unidic = './test/uni_dic.txt'
    write_sentence(test_path, test)
    write_sentence(ans_path, ans)
    write_sentence(train_path, train)
    LMdic(train_path, unidic)
    Bidic(train_path, Bi_dic)
