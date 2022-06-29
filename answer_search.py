#!/usr/bin/env python3
# coding: utf-8
# File: answer_search.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-10-5

from py2neo import Graph
from functools import cmp_to_key

class AnswerSearcher:
    def __init__(self):
        self.g = Graph(
            #host="127.0.0.1",
            #http_port=7474,
            "http://localhost:7474",
            user="neo4j",
            password="Anan0275")
        self.num_limit = 5

    
    '''执行cypher查询, 并返回相应结果'''
    def search_main(self, sqls, old_ans):
        final_answers = []
        for sql_ in sqls:
            question_type = sql_['question_type']
            queries = sql_['sql']
            #answers = []
            answers = old_ans
            tmps = []
            for query in queries:
                ress = self.g.run(query).data() #返回列表，元素为字典，key为指定要返回的
                #answers += ress
                #TODO: 改为取交集
                if answers:
                    for ans in answers: #ans为字典
                        for new in ress:
                            if ans['m.name'] == new['m.name']:
                                #tmps += ans
                                tmps.append(ans)
                    answers = tmps
                    tmps = []
                else:
                    answers = ress
            return {'question_type':question_type, 'answers':answers}

            '''final_answer = self.answer_prettify(question_type, answers)
            if final_answer:
                final_answers.append(final_answer)
        return final_answers'''

    '''查询推荐科室是否不超过2，否则继续询问病症'''
    def department_limitChk(self,answers):
        if not(answers):
            return{'flag':1, 'ans_all':[]}
        flag = 0
        ans_all = []
        dep_all = []
        for ans in answers:
            if ans['n.name'] in dep_all:
                for element in ans_all:
                    if element['department'] == ans['n.name']:
                        element['diseases'] == []
                        element['diseases'].append({'dis_name':ans['m.name'],'get_prob':ans['m.get_prob']})
            else:
                ans_all.append({'department':ans['n.name'],'diseases':[{'dis_name':ans['m.name'], 'get_prob':ans['m.get_prob']}]})
                dep_all.append(ans['n.name'])
                if len(dep_all) > 2:
                    flag = 1
                    break
        return {'flag':flag, 'ans_all':ans_all}

    


if __name__ == '__main__':
    searcher = AnswerSearcher()