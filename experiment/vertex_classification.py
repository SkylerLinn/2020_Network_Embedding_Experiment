#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @file   : node_prediction.py
# @author : Zhutian Lin
# @date   : 2019/10/17
# @version: 1.0
# @desc   : 完成点分类任务
import numpy as np
import logging
from gensim.models import Word2Vec
from sklearn.svm import SVC
from sklearn.metrics import f1_score
from gensim.models import KeyedVectors
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import util


class vertex_classification:
    def __init__(self):
        logging.info("初始化分类器")
        self.vectors_dict = {}  # 每个点对应的字典{点index(str):向量(nparray)} 这个str可不能带小数点
        self.node_dict = {}  # 每个点的label
        self.node_list = []  # 备选点
        self.X_train = []
        self.X_test = []
        self.y_train = []
        self.y_test = []

    # 操作：首先导入数据集，格式不变；原来的test_set输入为以空格为分隔符的node1 node2，主程序的embedding，格式不变

    def import_model(self, model_name, option=0):
        #  0代表主方法，model_name代表的是主函数输出的节点向量
        if option == 0:
            word_vectors = np.loadtxt(model_name, delimiter=' ')
            for line in word_vectors:
                tmp = {str(int(line[0])): line[1:-1]}
                self.vectors_dict.update(tmp)

            self.node_list = [node for node in self.vectors_dict]
        if option == 1:
            model = Word2Vec.load(model_name)
            word_vectors = KeyedVectors.load(model_name)

            # 构造新字典
            for key in word_vectors.wv.vocab.keys():
                tmp = {key: model.wv.__getitem__(key)}
                self.vectors_dict.update(tmp)
            self.node_list = [node for node in self.vectors_dict]

    def import_node(self, dsname):
        # 统一操作为str
        node_data = np.loadtxt(dsname, delimiter="\t").tolist()
        for edge in node_data:
            self.node_dict.update({str(int(edge[0])): str(int(edge[1]))})
            self.node_dict.update({str(int(edge[2])): str(int(edge[3]))})

    def build_train_test(self):
        logging.debug("build_train_test")
        vec = []
        label = []

        for node in self.vectors_dict:
            node_vec = self.vectors_dict.get(node)
            node_vec = node_vec.tolist()
            if node_vec is not None and self.node_dict.get(node) is not None:
                vec.append(node_vec)
                label.append(int(self.node_dict.get(node)))
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(vec, label, test_size=0.1)

    def classify(self):
        logging.debug("classify")
        lr = LogisticRegression(C=1000.0, random_state=0)
        lr.fit(self.X_train, self.y_train)
        Y_predict_lr = lr.predict(self.X_test).tolist()
        print("lr_micro", f1_score(self.y_test, Y_predict_lr, average='micro'))
        print("lr_weighted", f1_score(self.y_test, Y_predict_lr, average='weighted'))
        print("lr_micro", f1_score(self.y_test, Y_predict_lr, average='macro'))

        svm = SVC(kernel='linear', C=1000.0, random_state=0)
        svm.fit(self.X_train, self.y_train)
        Y_predict_svm = svm.predict(self.X_test).tolist()
        print("svm_micro", f1_score(self.y_test, Y_predict_svm, average='micro'))
        print("svm_weighted", f1_score(self.y_test, Y_predict_svm, average='weighted'))
        print("svm_macro", f1_score(self.y_test, Y_predict_svm, average='macro'))


if __name__ == '__main__':
    options, args = util.model_choice_dataset_args("classification")
    c = util.parse_model_name(options.m)

    nlf = vertex_classification()
    nlf.import_model(options.m, c)
    nlf.import_node(options.d)
    nlf.build_train_test()
    nlf.classify()
