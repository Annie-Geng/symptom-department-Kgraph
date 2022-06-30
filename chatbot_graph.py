#!/usr/bin/env python3
# coding: utf-8
# File: chatbot_graph.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-10-4

from question_classifier import *
from question_parser import *
from answer_search import *

old_ans = []

'''问答类'''
class ChatBotGraph:
    def __init__(self):
        self.classifier = QuestionClassifier()
        self.parser = QuestionPaser()
        self.searcher = AnswerSearcher()

    def chat_main(self, age, sex, sent):
        #answer = '您好，我是分诊小助手，很抱歉没能听懂您的病症；今后我会更加完善功能，请您先咨询人工分诊医生哦！'
        answer = '请问您是否还有其他不适或症状？'
        syno_words = 
        res_classify = self.classifier.classify(age, sex, sent)
        if not res_classify:
            return answer
        res_sql = self.parser.parser_main(res_classify)

        global old_ans
        search_dic = self.searcher.search_main(res_sql,old_ans)
        #search_dic 返回为空时？#应该是之前的错误，不太会空，因为有question type；是answer可能空
        #if not search_dic:
        #    return answer
        if not search_dic['answers']:
            return answer

        old_ans = search_dic['answers']
        question_type = search_dic['question_type']
        
        chk = self.searcher.department_limitChk(old_ans)
        if chk['flag'] and question_type != 'specific_dis':
            return answer
        else:
            final_answers = self.answer_prettify(question_type,chk['ans_all'])
            return '\n'.join(final_answers)
    
    '''根据对应的qustion_type, 调用相应的回复模板'''
    def answer_prettify(self, question_type, answers):
        final_answer = []
        
        #sorted_ans = sorted(answers, key= lambda x: x['get_prob'],reverse = True)
        sorted_ans = answers
        #final_ans = ''
        if question_type == 'specific_dis':
            #TODO: 应该按可能性排序，而不是直接set
            for ans in sorted_ans:
                half_ans = ''
                final_ans = ''
                for dis in ans["diseases"]:
                    half_ans += '您患“{0}”(患病率：{1}) '.format(dis['dis_name'], dis['get_prob'])
                final_ans += half_ans
                final_ans += '推荐去“{0}”就诊。\n'.format(ans['department'])
                final_answer.append(final_ans)
                
        else:
            
            for ans in sorted_ans:
                half_ans = ''
                final_ans = ''
                for dis in ans["diseases"]:
                    half_ans += '您可能患“{0}”(患病率：{1}) '.format(dis['dis_name'], dis['get_prob'])
                final_ans += half_ans
                final_ans += '推荐去“{0}”就诊。\n'.format(ans['department'])
                final_answer.append(final_ans)

        return final_answer

if __name__ == '__main__':
    handler = ChatBotGraph()
    while 1:
        print('您好，我是分诊小助手。请说明您的不适症状或所患疾病，我会帮您自动分诊！')
        age = input('请输入您的年龄:')
        sex = input('请输入您的性别：')
        count = 0
        flag = 1
        old_ans = []
        while flag:
            question = input('患者:')
            answer = handler.chat_main(age, sex, question)
            if answer == '请问您是否还有其他不适或症状？':
                if count > 4:
                    print('分诊小助手:很抱歉没能听懂您的病症；今后我会更加完善功能，请您先咨询人工分诊医生哦！\n')
                    flag = 0
                else:
                    print('分诊小助手:', answer[:-1])
                    count += 1
            else:
                print('分诊小助手:', answer[:-1])
                print('如仍有其他问题，请联系工作医生！\n')
                flag = 0
            

