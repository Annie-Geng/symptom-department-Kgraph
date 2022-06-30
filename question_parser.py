#!/usr/bin/env python3
# coding: utf-8
# File: question_parser.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-10-4

class QuestionPaser:

    '''构建实体节点'''  #互换键值对 #e.g.{'disease':['感冒','百日咳'],'department':['内科']}
    def build_entitydict(self, args):
        entity_dict = {}
        for arg, types in args.items():
            for type in types:
                if type not in entity_dict:
                    entity_dict[type] = [arg]
                else:
                    entity_dict[type].append(arg)

        return entity_dict

    '''解析主函数'''
    def parser_main(self, res_classify):
        args = res_classify['args']     #e.g.{'百日咳':'disease','感冒':'disease','内科':'department'}
        entity_dict = self.build_entitydict(args)
        question_types = res_classify['question_types']
        sqls = []   #列表元素是sql_类型的字典
        for question_type in question_types:
            sql_ = {}   #sql_类型的字典包含key:'question_type','sql'(sql查询语句，由sql_transfer函数生成)
            sql_['question_type'] = question_type
            sql = []
            
            if (question_type == 'child_sym') or (question_type == 'female_sym') or (question_type == 'male_sym') or (question_type == 'sym'):                
                sql = self.sql_transfer(question_type, entity_dict.get('symptom'))

            else:
                sql = self.sql_transfer(question_type, entity_dict.get('disease'))    

            if sql:
                sql_['sql'] = sql

                sqls.append(sql_)

        return sqls

    '''针对不同的问题，分开进行处理'''
    def sql_transfer(self, question_type, entities):
        #if not entities:
        #    return []

        # 查询语句
        sql = []

        # 查询疾病有哪些症状
        if question_type == 'specific_dis':
            #sql = ["MATCH (m:Disease)-[r:belongs_to]->(n:Department) where m.name CONTAINS '{0}' return m.name, m.get_prob, r.name, n.name".format(i) for i in entities]
            sql = ["MATCH (m:Disease)-[r:belongs_to]->(n:Department) where m.name = '{0}' return m.name, m.get_prob, r.name, n.name".format(i) for i in entities]

        elif question_type == 'infant': #TODO:具体看数据细分到什么程度，需要疾病还是直接分到一个诊室
            sql = ["MATCH (n:Department) where n.name CONTAINS '新生儿' return n.name"] #TODO: 是否叫新生儿科？

        elif  question_type == 'child_dis':
            sql = ["MATCH (m:Disease)-[r:belongs_to]->(n:Department) where m.name CONTAINS '{0}' AND n.name CONTAINS '儿' AND NOT n.name CONTAINS '新生儿' return m.name, m.get_prob, r.name, n.name".format(i) for i in entities]

        elif  question_type == 'child_sym':
            sql = ["MATCH (p:Symptom)<-[r2:has_symptom]-(m:Disease)-[r1:belongs_to]->(n:Department) where p.name CONTAINS '{0}' AND n.name CONTAINS '儿' AND NOT n.name CONTAINS '新生儿' return p.name, r2.name, m.name,m.get_prob, r1.name, n.name".format(i) for i in entities]

        elif  question_type == 'female_dis':
            sql = ["MATCH (m:Disease)-[r:belongs_to]->(n:Department) where m.name CONTAINS '{0}' AND NOT n.name CONTAINS '男' AND NOT n.name CONTAINS '儿' return m.name, m.get_prob, r.name, n.name".format(i) for i in entities]

        elif  question_type == 'female_sym':
            sql = ["MATCH (p:Symptom)<-[r2:has_symptom]-(m:Disease)-[r1:belongs_to]->(n:Department) where p.name CONTAINS '{0}' AND NOT n.name CONTAINS '男' AND NOT n.name CONTAINS '儿' return p.name, r2.name, m.name,m.get_prob, r1.name, n.name".format(i) for i in entities]

        elif  question_type == 'male_dis':
            sql = ["MATCH (m:Disease)-[r:belongs_to]->(n:Department) where m.name CONTAINS '{0}' AND NOT n.name CONTAINS '妇' AND NOT n.name CONTAINS '产' AND NOT n.name CONTAINS '儿' return m.name, m.get_prob, r.name, n.name".format(i) for i in entities]

        elif  question_type == 'male_sym':
            sql = ["MATCH (p:Symptom)<-[r2:has_symptom]-(m:Disease)-[r1:belongs_to]->(n:Department) where p.name CONTAINS '{0}' AND NOT n.name CONTAINS '妇' AND NOT n.name CONTAINS '产' AND NOT n.name CONTAINS '儿' return p.name, r2.name, m.name,m.get_prob, r1.name, n.name".format(i) for i in entities]

        elif  question_type == 'dis':
            sql = ["MATCH (m:Disease)-[r:belongs_to]->(n:Department) where m.name CONTAINS '{0}' return m.name, m.get_prob, r.name, n.name".format(i) for i in entities]

        elif  question_type == 'sym':
            sql = ["MATCH (p:Symptom)<-[r2:has_symptom]-(m:Disease)-[r1:belongs_to]->(n:Department) where p.name CONTAINS '{0}' return p.name, r2.name, m.name,m.get_prob, r1.name, n.name".format(i) for i in entities]

        return sql



if __name__ == '__main__':
    handler = QuestionPaser()
