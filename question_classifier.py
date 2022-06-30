#!/usr/bin/env python3
# coding: utf-8
# File: question_classifier.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-10-4

import os
import ahocorasick
import re

class QuestionClassifier:
    def __init__(self):
        cur_dir = '\\'.join(os.path.abspath(__file__).split('\\')[:-1])
        #　特征词路径
        self.disease_path = os.path.join(cur_dir, 'dict\\disease.txt')
        self.department_path = os.path.join(cur_dir, 'dict\\department.txt')
        self.symptom_path = os.path.join(cur_dir, 'dict\\symptom.txt')
        #self.deny_path = os.path.join(cur_dir, 'dict/deny.txt')

        # 加载特征词
        self.disease_wds= [i.strip() for i in open(self.disease_path, encoding='utf-8') if i.strip()]
        self.department_wds= [i.strip() for i in open(self.department_path, encoding='utf-8') if i.strip()]
        self.symptom_wds= [i.strip() for i in open(self.symptom_path, encoding='utf-8') if i.strip()]
        self.region_words = set(self.department_wds + self.disease_wds + self.symptom_wds) #合在一起并去重
        #self.deny_words = [i.strip() for i in open(self.deny_path, encoding='utf-8') if i.strip()]

        # 构造领域actree
        self.region_tree = self.build_actree(list(self.region_words))
        # 构建词典
        self.wdtype_dict = self.build_wdtype_dict()

        # 问句疑问词
        #self.symptom_qwds = ['症状', '表征', '现象', '症候', '表现']
        #self.acompany_qwds = ['并发症', '并发', '一起发生', '一并发生', '一起出现', '一并出现', '一同发生', '一同出现', '伴随发生', '伴随', '共现', '还']
        #self.belong_qwds = ['属于什么科', '属于', '去', '挂', '什么科', '科室', '诊室', '挂什么科', '什么科室', '去什么科室','去什么科', '挂什么号', '挂号']
        self.doubt_qwds = ['有没有可能', '是不是', '会不会', '会不会是', '也许', '大概', '可能']
        self.female = ['女', '女性', '女孩', '女童', '女婴', '妇女', '孕妇', '产妇', 'woman', 'women', 'female', 'f', 'F']
        self.male = ['男', '男性', '男孩', '男童', '男婴', 'man', 'men', 'male', 'm', 'M']

        #print('model init finished ......')

        return

    '''分类主函数'''    #我的项目只有两种1."symptom_department" 2."disease_department" 1需要借助2完成
    def classify(self, age, sex, question):
        data = {}
        medical_dict = self.check_medical(question)
        if not medical_dict:
            return {}
        data['args'] = medical_dict
        #收集问句当中所涉及到的实体类型
        types = []
        for type_ in medical_dict.values():
            types += type_
        #question_type = 'others'

        question_types = []

        # 疾病--诊室
        '''if self.check_words(self.belong_qwds, question) and ('disease' in types):
            question_type = 'disease_department'
            question_types.append(question_type)
        # 症状--诊室
        if self.check_words(self.symptom_qwds, question) and ('symptom' in types):
            question_type = 'symptom_department'
            question_types.append(question_type)

        
        # 并发症
        if self.check_words(self.acompany_qwds, question) and ('disease' in types):
            question_type = 'disease_acompany'
            question_types.append(question_type)

        # 若没有查到相关的外部查询信息，那么则将该疾病的描述信息返回
        if question_types == [] and 'disease' in types:
            question_types = ['disease_desc']

        # 若没有查到相关的外部查询信息，那么则将该疾病的描述信息返回
        if question_types == [] and 'symptom' in types:
            question_types = ['symptom_disease']'''
        
        if ('disease' in types) and not (self.check_words(self.doubt_qwds, question)): #基本不存在
            question_types.append('specific_dis')
        else:
            if self.group_age(age) == 'infant': #TODO: 具体看数据细分到什么程度，需要疾病还是直接分到一个诊室
                question_types.append('infant')
            elif self.group_age(age) == 'child': #TODO: 具体看数据细分到什么程度，需要疾病还是直接分到一个诊室
                if 'disease' in types:
                    question_types.append('child_dis')
                if 'symptom' in types:
                    question_types.append('child_sym')
            else:
                if self.check_words(self.female, sex):
                    if 'disease' in types:
                        question_types.append('female_dis')
                    if 'symptom' in types:
                        question_types.append('female_sym')
                elif self.check_words(self.male, sex):
                    if 'disease' in types:
                        question_types.append('male_dis')
                    if 'symptom' in types:
                        question_types.append('male_sym')
                else:
                    if 'disease' in types:
                        question_types.append('dis')
                    if 'symptom' in types:
                        question_types.append('sym')
            
        # 将多个分类结果进行合并处理，组装成一个字典
        data['question_types'] = question_types

        return data

    '''构造词对应的类型'''  #字典中每个专有名词为key,对应分类：疾病/科室...为value
    def build_wdtype_dict(self):
        wd_dict = dict()
        for wd in self.region_words:
            wd_dict[wd] = []
            if wd in self.disease_wds:
                wd_dict[wd].append('disease')
            if wd in self.department_wds:
                wd_dict[wd].append('department')
            if wd in self.symptom_wds:
                wd_dict[wd].append('symptom')
        return wd_dict

    '''构造actree, 加速过滤'''  #? to understand
    def build_actree(self, wordlist):
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree

    '''问句过滤'''
    def check_medical(self, question):
        region_wds = []
        for i in self.region_tree.iter(question):
            wd = i[1][1]
            region_wds.append(wd)
        stop_wds = []
        for wd1 in region_wds:
            for wd2 in region_wds:
                if wd1 in wd2 and wd1 != wd2:
                    stop_wds.append(wd1)    #短词包含在长词中，stop_wds为短词
        final_wds = [i for i in region_wds if i not in stop_wds]    #只保留长词，舍弃短词
        final_dict = {i:self.wdtype_dict.get(i) for i in final_wds} #得到字典，为build_wdtype_dict中问题出现部分的子集

        return final_dict

    '''基于特征词进行分类'''
    def check_words(self, wds, sent):
        for wd in wds:
            if wd in sent:
                return True
        return False
    
    '''对年龄进行分类：0~1岁：infant；1~14岁：child；15岁及以上：adult'''
    def group_age(self, age):
        age_dic = {}
        quants = [i for i in age if not(str.isdigit(i))] #e.g. 天，周，月，岁
        if not(quants):
            age_dic['岁'] = int(age)
        else:
            ages = []
            ages = re.findall("\d+\.?\d*", age)  # 正则表达式
            for i in range(len(quants)):
                age_dic[quants[i]] = float(ages[i])
        
        if '岁' not in age_dic:
            return 'infant'
        elif age_dic['岁'] < 15:
            return 'child'
        else:
            return 'adult'


if __name__ == '__main__':
    handler = QuestionClassifier()
    while 1:
        question = input('input an question:')
        data = handler.classify(question)
        print(data)