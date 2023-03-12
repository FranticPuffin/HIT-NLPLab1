"""
本文件用于测试未登录词识别算法
"""
import Bi_LM
import HMM
import Uni_LM
import Value


def main():
    text_path = '199801_03_train.txt'  # 训练集
    test_path = '199801_03_test.txt'  # 待分词文本
    ans_path = '199801_03_ans.txt'  # 分词答案
    ans = Value.PreProcess(ans_path)
    # 若已经训练完，则可将此处训练代码注释掉
    train = HMM.HMMTRAIN()
    res_path = 'hmm_test.pkl'
    train.tag_text(res_path, text_path)
    Hmm = HMM.HMM(res_path)
    Uni_LM_ans_path = 'Uni_ans.txt'
    Bi_ans_path = 'Bi_ans.txt'
    Bi_dic_path = 'Bidic.txt'
    Uni_dic_path = 'uni_dic.txt'
    Bi_LM.Bi_seg(Hmm, test_path, Uni_dic_path, Bi_dic_path, Bi_ans_path)
    bi_OOV = Value.PreProcess(Bi_ans_path)
    print('LM_Bi算法的准确率、召回率、f值为：', Value.calculate(ans, bi_OOV))
    Uni_LM.Uni_seg(test_path, Uni_dic_path, Uni_LM_ans_path)
    lm = Value.PreProcess(Uni_LM_ans_path)
    print('LM_Uni算法的准确率、召回率、f值为：', Value.calculate(ans, lm))


if __name__ == '__main__':
    main()
