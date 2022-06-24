#!/usr/bin/env python3
# coding: utf-8
# File: MedicalGraph.py
# Author: Shuangyue Geng
# Date: 22-4-26

import os
import json
from py2neo import Graph,Node

class MedicalGraph:
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        self.data_path = os.path.join(cur_dir, 'data/medical.json') #得到json文件路径
        self.g = Graph(
            #host="127.0.0.1",  # neo4j 搭载服务器的ip地址，ifconfig可获取到
            "http://localhost:7474",  # neo4j 服务器监听的端口号
            user="neo4j",  # 数据库user name，如果没有更改过，应该是neo4j
            password="Anan0275")

    '''读取文件'''
    def read_nodes(self):
        # 共3类节点
        departments = []    #科室
        diseases = []   #疾病
        symptoms = []   #症状

        disease_infos = []  #疾病信息   #每种疾病一个字典，是字典为元素的列表   #75行 disease_infos.append(disease_dict)

        # 构建节点实体关系
        rels_department = [] #　科室－科室关系
        rels_symptom = [] #疾病症状关系
        rels_acompany = [] # 疾病并发关系
        rels_category = [] #　疾病与科室之间的关系


        count = 0
        for data in open(self.data_path, encoding='utf-8'): #打开json文件
            disease_dict = {}
            count += 1
            print(count)
            data_json = json.loads(data)    #需要json库，将json转换为py对象
            disease = data_json['name']
            disease_dict['name'] = disease
            diseases.append(disease)
            disease_dict['cure_department'] = ''
            disease_dict['symptom'] = ''
            disease_dict['cured_prob'] = ''

            if 'symptom' in data_json:
                symptoms += data_json['symptom']
                for symptom in data_json['symptom']:
                    rels_symptom.append([disease, symptom])

            if 'acompany' in data_json:
                for acompany in data_json['acompany']:
                    rels_acompany.append([disease, acompany])

            if 'get_prob' in data_json:
                disease_dict['get_prob'] = data_json['get_prob']

            if 'cure_department' in data_json:
                cure_department = data_json['cure_department']
                if len(cure_department) == 1:   #只有一个相关诊室
                     rels_category.append([disease, cure_department[0]])
                if len(cure_department) == 2:   #分为大类诊室和小类诊室
                    big = cure_department[0]
                    small = cure_department[1]
                    rels_department.append([small, big])
                    rels_category.append([disease, small])

                disease_dict['cure_department'] = cure_department
                departments += cure_department

            disease_infos.append(disease_dict)

        return set(departments), set(symptoms), set(diseases), disease_infos,\
               rels_department, rels_symptom, rels_acompany, rels_category   #set去除重复元素

    '''建立节点'''  #一般节点
    def create_node(self, label, nodes):
        count = 0
        for node_name in nodes:
            node = Node(label, name=node_name)
            self.g.create(node)
            count += 1
            print(count, 'of', len(nodes))
        return

    '''创建知识图谱中心疾病的节点'''    #疾病节点，属性更多
    def create_diseases_nodes(self, disease_infos):
        count = 0
        for disease_dict in disease_infos:
            node = Node("Disease", name=disease_dict['name'], get_prob=disease_dict['get_prob']) #创建节点，包含多个属性
            self.g.create(node)
            count += 1
            print(count, 'of', len(disease_infos))
        return

    '''创建知识图谱实体节点类型schema'''
    def create_graphnodes(self):
        Departments, Symptoms, Diseases, disease_infos, rels_department, rels_symptom, rels_acompany, rels_category = self.read_nodes()
        self.create_diseases_nodes(disease_infos)
        print(len(disease_infos), 'disease_infos have been created!')
        self.create_node('Department', Departments)
        print(len(Departments), 'Departments have been created!')
        self.create_node('Symptom', Symptoms)
        print(len(Symptoms), 'Symptoms have been created!')
        return


    '''创建实体关系边'''
    def create_graphrels(self):
        Departments, Symptoms, Diseases, disease_infos, rels_department, rels_symptom, rels_acompany, rels_category = self.read_nodes()
        self.create_relationship('Department', 'Department', rels_department, 'belongs_to', '属于') #细分诊室 属于 大类诊室
        self.create_relationship('Disease', 'Symptom', rels_symptom, 'has_symptom', '症状')
        self.create_relationship('Disease', 'Disease', rels_acompany, 'acompany_with', '并发症')
        self.create_relationship('Disease', 'Department', rels_category, 'belongs_to', '所属科室')  #疾病所属细分科室

    '''创建实体关联边'''
    def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        count = 0
        # 去重处理
        set_edges = []
        for edge in edges:
            set_edges.append('###'.join(edge))
        all = len(set(set_edges))
        for edge in set(set_edges):
            edge = edge.split('###')
            p = edge[0]
            q = edge[1]
            query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, rel_name)
            try:
                self.g.run(query)
                count += 1
                print(rel_type, count, all)
            except Exception as e:
                print(e)
        return

    '''导出数据'''  #to do
    def export_data(self):  #主函数没调用，文件夹放的是用这个调用生成好的了
        Departments, Symptoms, Diseases, disease_infos, rels_department, rels_symptom, rels_acompany, rels_category = self.read_nodes()

        f_department = open('department.txt', 'w+')
        f_symptom = open('symptom.txt', 'w+')
        f_disease = open('disease.txt', 'w+')

        f_department.write('\n'.join(list(Departments)))
        f_symptom.write('\n'.join(list(Symptoms)))
        f_disease.write('\n'.join(list(Diseases)))

        f_department.close()
        f_symptom.close()
        f_disease.close()

        return



if __name__ == '__main__':
    handler = MedicalGraph()
    print("step1:导入图谱节点中")
    #handler.create_graphnodes()
    print("step2:导入图谱边中")      
    #handler.create_graphrels()
    #handler.export_data()
