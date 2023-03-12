import pickle
import re
from math import log

send = {'B': 'ES', 'M': 'MB', 'E': 'BM', 'S': 'SE'}
MIN = -3.14e+20
locates = ['B', 'M', 'E', 'S']


class HMM():
    def __init__(self, model_path):
        """
        初始化HMM,HMM三个参数，分别为初始状态集、状态转移概率、发射概率
        :param model_path: 模型存储地址
        """
        self.pi = {}  # 初始状态集
        self.A = {}  # 状态转移概率
        self.B = {}  # 发射概率
        file = open(model_path, 'rb')
        try:
            self.pi = pickle.load(file)
            self.A = pickle.load(file)
            self.B = pickle.load(file)
        finally:
            file.close()

    def viterbi(self, sentence):
        """
        利用维特比算法对待分词文本标注BEMS
        :param sentence: 待分词文本
        :return:
        """
        way = {}  # 存储路径
        best_choice = [{}]  # 存储到达每一个位置的时候的最优选择及其对应的值
        for locate in locates:
            best_choice[0][locate] = self.B[locate].get(sentence[0], MIN) + self.pi[locate]
            way[locate] = [locate]
        if len(sentence) == 0:
            return 0, {}
        for i, word in enumerate(sentence[1:]):
            best_choice.append({})
            temp_path = {}
            for locate in locates:
                emit = self.B[locate].get(sentence[i], MIN)
                cost = MIN
                cur_state = ''
                for s in send[locate]:
                    temp = best_choice[i - 1][s] + emit + self.A[s].get(locate, MIN)
                    if temp > cost:
                        cost = temp
                        cur_state = s
                temp_path[locate] = way[cur_state] + [locate]
                best_choice[i][locate] = cost
            way = temp_path
        # 遍历ES的词，因为只有ES可能出现在词的末尾
        (cost, locate) = max([(best_choice[len(sentence) - 1][state], state) for state in 'ES'])
        return cost, way[locate]

    def word_seg(self, words):
        """
        处理连续输入的单字的分词，例如分词为我，你，好，改为我，你好
        :param words:需要处理的单字
        :return:分词结果
        """
        if len(words) == 1:
            return [words]
        seg_list = self.viterbi(words)[1]
        result = ''
        for i, word in enumerate(words):
            tag = seg_list[i]
            if tag == 'E' or tag == 'S':
                result += word + '/'
            elif tag == 'B' or tag == 'M':
                result += word
        result = result.rstrip()
        result = result.split('/')[0:-1]
        return result

    def seg_line(self, word_list, sentence_seg=[]):
        """
        对已经处理过的句子进行分词，句子形如[w1,w2,w3w4w5]
        :param word_list: 需要进一步分词的句子
        :param sentence_seg: 分词结果
        :return:分词结果
        """
        operate = ''
        for i, word in enumerate(word_list):
            if operate:
                for op in self.word_seg(operate):
                    sentence_seg.append(op)
                operate = ''
            sentence_seg.append(word)
        return sentence_seg

    def hmm(self, text_path, io_path):
        """
        使用HMM对文本进行分词
        :param text_path: 需要分词的文本所在地址
        :param io_path:分词结果输出地址
        :return:
        """
        file = open(text_path, 'r', encoding='utf-8')
        try:
            text = file.read().split('\n')
        finally:
            file.close()
        seg = []
        for sentence in text:
            if sentence == '':
                continue
            sentence = sentence.strip()
            sentence_seg = []
            if len(sentence) != 0:
                ##处理开头的时间信息
                if re.findall('[0-9]{8}-[0-9]{2}-[0-9]{3}-[0-9]{3}', sentence):
                    sentence_seg.append(sentence[:19])
                    sentence = sentence[19:]
                sentence = list(sentence)
                sentence_seg = self.seg_line(sentence, sentence_seg)
                seg.append(sentence_seg)
        file = open(io_path, 'w', encoding='utf-8')
        try:
            for sentence in seg:
                if sentence == '':
                    continue
                file.write('\ '.join(sentence) + '\ \n')
        finally:
            file.close()


class HMMTRAIN():
    """
    使用EM算法对HMM的参数进行训练
    """

    def __init__(self):
        self.sentence_nums = 0  # 统计句子数
        self.word_dic = set()  # 保存出现过的词
        self.state_times = {}  # 记录每一个状态出现的次数
        self.pi = {}  # 初始状态集
        self.A = {}  # 状态转移概率
        self.B = {}  # 发射概率
        for state in locates:
            self.state_times[state] = 0.0
            self.pi[state] = 0.0
            self.A[state] = {}
            self.B[state] = {}
            for temp_state in locates:
                self.A[state][temp_state] = 0.0  # state->temp_state的转移概率初始化

    def line_tag(self, line):
        """
        给句子做出标注，返回句子中每一个字对应的词位
        :param line:需要标注的句子
        :return:标注结果
        """
        sentence = []
        tag = ''
        for i, word in enumerate(line.split()):
            if word[0] == '[':
                word = word[1:word.index('/')]
            else:
                word = word[0:word.index('/')]
            self.sentence_nums += 1
            if len(word) == 0:
                continue
            if ']' in word:
                word = word.split(']')[0]
            sentence.extend(list(word))
            self.word_dic.add(word)
            # 单独记录句首状态
            if i == 0 and len(word) == 1:
                self.pi['S'] += 1
            elif i == 0 and len(word) != 1:
                self.pi['B'] += 1
            if len(word) == 1:
                tag += 'S'
            else:
                # 该词为BM*E的形式，则加入BM*E
                tag += 'B'
                tag += 'M' * (len(word) - 2)
                tag += 'E'
        return sentence, tag

    def train_tag(self, text_path):
        """
        训练参数
        :param text_path: 训练集
        :return: 无，更改转移概率等
        """
        file = open(text_path, 'r', encoding='utf-8')
        try:
            text = file.read().split('\n')
        finally:
            file.close()
        for line in text:
            if line == '':
                continue
            # 去除时间
            line = line[19:]
            word, tag = self.line_tag(line)
            for i in range(len(tag)):
                self.state_times[tag[i]] += 1
                self.B[tag[i]][word[i]] = self.B[tag[i]].get(word[i], 0) + 1  # 发射概率
                if i > 0:  # 转移概率
                    self.A[tag[i - 1]][tag[i]] += 1

    def tag_text(self, res_path, text_path, text_path2='', text_path3='', text_path4=''):
        """
        通过标注整个文本来训练参数（pi，A，B）
        :param res_path: 参数写入的地址
        :param text_path: 需要标注的文本的地址
        :param text_path2: 需要标注的文本的地址2
        :param text_path3: 需要标注的文本的地址3
        :param text_path4: 需要标注的文本的地址4
        :return: 训练出的参数写入文本文件
        """
        self.train_tag(text_path)
        if text_path2 != '':
            self.train_tag(text_path2)
        if text_path3 != '':
            self.train_tag(text_path3)
        if text_path4 != '':
            self.train_tag(text_path4)
        ##更新参数
        for state in locates:
            if self.pi[state] == 0:
                self.pi[state] = MIN
            else:
                self.pi[state] = log(self.pi[state] / self.sentence_nums)
            for temp_state in locates:
                if self.A[state][temp_state] == 0:
                    self.A[state][temp_state] = MIN
                else:
                    self.A[state][temp_state] = log(self.A[state][temp_state] / self.state_times[state])
            for word in self.B[state].keys():
                self.B[state][word] = log(self.B[state][word] / self.state_times[state])
        file = open(res_path, 'wb')
        try:
            pickle.dump(self.pi, file)
            pickle.dump(self.A, file)
            pickle.dump(self.B, file)
        finally:
            file.close()


if __name__ == '__main__':
    train = HMMTRAIN()
    text_path = './DataSet/199801_seg&pos.txt'
    text_path2 = './DataSet/199802.txt'
    text_path3 = './DataSet/199803.txt'
    text_path4 = './DataSet/name.txt'
    res_path = './ans/hmm_pickle.pkl'
    train.tag_text(res_path, text_path, text_path2, text_path3, text_path4)
