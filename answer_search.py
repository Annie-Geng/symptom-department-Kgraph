#!/usr/bin/env python3
# coding: utf-8
# File: answer_search.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-10-5

from py2neo import Graph
from functools import cmp_to_key

'''def proc(ans):
    get_prob = ans['m.get_prob']
    key = ''
    index = get_prob.find('%')
    if index != -1:
        for i in reversed(get_prob)[1:]:
            if i.isdigit:
                key += i
            else:
                break
        key = reversed(key)
    else:
        key = get_prob
    
    return key'''


class AnswerSearcher:
    def __init__(self):
        self.g = Graph(
            #host="127.0.0.1",
            #http_port=7474,
            "http://localhost:7474",
            user="neo4j",
            password="Anan0275")
        self.num_limit = 5

    '''def cmp(prob1,prob2):
        a = proc(prob1[1])
        b = proc(prob2[1])
        if (not(a.isdigit) and not(b.isdigit)) or (a.isdigit and b.isdigit):
                return (a - b)
        else:
            if a.isdigit:
                return -1
            else:
                return 1'''

    '''执行cypher查询, 并返回相应结果'''
    def search_main(self, sqls):
        final_answers = []
        for sql_ in sqls:
            question_type = sql_['question_type']
            queries = sql_['sql']
            answers = []
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

            final_answer = self.answer_prettify(question_type, answers)
            if final_answer:
                final_answers.append(final_answer)
        return final_answers

    '''根据对应的qustion_type, 调用相应的回复模板'''
    def answer_prettify(self, question_type, answers):
        final_answer = []
        if not answers:
            return ''
        '''if question_type == 'disease_symptom':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的症状包括：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'symptom_disease':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '症状{0}可能染上的疾病有：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_cause':
            desc = [i['m.cause'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}可能的成因有：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_prevent':
            desc = [i['m.prevent'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的预防措施包括：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_lasttime':
            desc = [i['m.cure_lasttime'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}治疗可能持续的周期为：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_cureway':
            desc = [';'.join(i['m.cure_way']) for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}可以尝试如下治疗：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_cureprob':
            desc = [i['m.cured_prob'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}治愈的概率为（仅供参考）：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_easyget':
            desc = [i['m.easy_get'] for i in answers]
            subject = answers[0]['m.name']

            final_answer = '{0}的易感人群包括：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_desc':
            desc = [i['m.desc'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0},熟悉一下：{1}'.format(subject,  '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_acompany':
            desc1 = [i['n.name'] for i in answers]
            desc2 = [i['m.name'] for i in answers]
            subject = answers[0]['m.name']
            desc = [i for i in desc1 + desc2 if i != subject]
            final_answer = '{0}的症状包括：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_not_food':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}忌食的食物包括有：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_do_food':
            do_desc = [i['n.name'] for i in answers if i['r.name'] == '宜吃']
            recommand_desc = [i['n.name'] for i in answers if i['r.name'] == '推荐食谱']
            subject = answers[0]['m.name']
            final_answer = '{0}宜食的食物包括有：{1}\n推荐食谱包括有：{2}'.format(subject, ';'.join(list(set(do_desc))[:self.num_limit]), ';'.join(list(set(recommand_desc))[:self.num_limit]))

        elif question_type == 'food_not_disease':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '患有{0}的人最好不要吃{1}'.format('；'.join(list(set(desc))[:self.num_limit]), subject)

        elif question_type == 'food_do_disease':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '患有{0}的人建议多试试{1}'.format('；'.join(list(set(desc))[:self.num_limit]), subject)

        elif question_type == 'disease_drug':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}通常的使用的药品包括：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'drug_disease':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '{0}主治的疾病有{1},可以试试'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'disease_check':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}通常可以通过以下方式检查出来：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

        elif question_type == 'check_disease':
            desc = [i['m.name'] for i in answers]
            subject = answers[0]['n.name']
            final_answer = '通常可以通过{0}检查出来的疾病有{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))'''

        sorted_ans = sorted(answers, key= lambda x: x['m.get_prob'],reverse = True)
        final_answer = ''
        if question_type == 'disease_department':
            '''departments = [i['n.name'] for i in answers]
            #disease = answers[0]['m.name']
            diseases = [i['m.name'] for i in answers]
            #final_answer = '您患“{0}”推荐去“{1}”就诊。'.format(disease, '、'.join(list(set(departments))[:self.num_limit]))
            for i in range(len(diseases)):
                final_answer += '您患“{0}”推荐去“{1}”就诊。\n'.format(diseases[i], departments[i])'''
            #TODO: 应该按可能性排序，而不是直接set
            '''sorted_ans = sorted(answers, key= lambda x: x['m.get_prob'],reverse = True)
            final_answer = '' '''
            for i in sorted_ans:
                final_answer += '您患“{0}”(患病率：{1})推荐去“{2}”就诊。\n'.format(i['m.name'],i['m.get_prob'],i['n.name'])
                
        elif question_type == 'symptom_department':
            '''departments = [i['n.name'] for i in answers]
            diseases = [i['m.name'] for i in answers]
            #symptoms = [i['p.name'] for i in answers]
            final_answer = '' '''
            '''for disease in diseases:
                final_answer += '您可能患 {0} 推荐去 {1} 就诊。\n'.format(disease, '、'.join(list(set(departments))[:self.num_limit]))'''
            '''for i in range(len(diseases)):
                final_answer += '您可能患“{0}”推荐去“{1}”就诊。\n'.format(diseases[i], departments[i])'''
            for i in sorted_ans:
                final_answer += '您可能患“{0}”(患病率：{1})推荐去“{2}”就诊。\n'.format(i['m.name'],i['m.get_prob'],i['n.name'])

        return final_answer


if __name__ == '__main__':
    searcher = AnswerSearcher()