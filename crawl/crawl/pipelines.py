# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from crawl.items import ProblemItem,StatusItem
from vj.models import *
import traceback


class SolPipeline(object):

    def __init__(self):
        print("<<<<<<<<<<<<<<<pipeline init>>>>>>>>>>>>")

    def process_item(self, item, spider):
        print(">>>>pipeline process")
        if isinstance(item,ProblemItem):
            print(">>>>ProblemItem")
            self.processProblemItem(item)
        elif isinstance(item,StatusItem):
            print(">>>>StatusItem")
            self.processStatusItem(item)
        return item

    def processStatusItem(self,item):
        try:
            print("begin : %s)))"%(item['vjRunID']))
            sts = Status.objects.get(runid=int(item['vjRunID']))
            sts.result = item['result']
            sts.timec = item['timec']
            sts.memoryc = item['memoryc']
            print("end : %s,%s,%s)))"%(sts.result,sts.timec,sts.memoryc))
            sts.save()
        except Exception as e:
            print("Error : sql execute failed")
            print(str(e))
            print('traceback.print_exc():%s'% traceback.print_exc())
            print('traceback.format_exc():\n%s' % traceback.format_exc())

    def processProblemItem(self,item):
        need = ['desc','input','output']
        for k in need :
            str = item[k]
            L = 0
            R = len(str)
            while L < R:
                if str[L] == '>':
                    break
                else:
                    L+=1
            while L < R:
                if str[R-1] == '<':
                    break;
                else:
                    R-=1
            item[k] = str[L+1:R-1]

        for k in item.keys():
            str = ""
            for i in range(0,len(item[k])):
                if item[k][i] == '\'':
                    str += '\\'
                str += item[k][i]
            item[k] = str

        try:
            try:
                prob = Problem.objects.get(originoj=item['originOj'],problemid=item['problemId'])
                print("The problem is existed.")
                prob.problemurl = item['problemUrl']
                prob.title = item['title']
                prob.timelimit = item['timeLimit']
                prob.memorylimit = item['memoryLimit']
                prob.description = item['desc']
                prob.input = item['input']
                prob.output = item['output']
                prob.sampleinput = item['sampleInput']
                prob.sampleoutput = item['sampleOutput']
                prob.updatetime = item['updateTime']
                prob.note = item['note']
                prob.save()

            except:
                print("The problem is not existed.")
                prob = Problem(originoj=item['originOj'],\
                    problemid=item['problemId'],\
                    problemurl=item['problemUrl'],\
                    title=item['title'],\
                    timelimit=item['timeLimit'],\
                    memorylimit=item['memoryLimit'],
                    description=item['desc'],\
                    input=item['input'],\
                    output=item['output'],\
                    sampleinput=item['sampleInput'],\
                    sampleoutput=item['sampleOutput'],\
                    updatetime=item['updateTime'],
                    note=item['note'])
                qs = Problem.objects.all()
                if not qs.exists():
                    prob.proid = 100000
                prob.save()
        except Exception as e:
            print.write("Error : sql execute failed")
            print.write(str(e))
            print.write('traceback.print_exc():%s'% traceback.print_exc())
            print.write('traceback.format_exc():\n%s' % traceback.format_exc())
            
