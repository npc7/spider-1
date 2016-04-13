#encoding=utf8
'''
Created on 2014-9-10
@author: jzx
'''
from lxml import etree
from lxml import html
import json
from logger import msgPrint
from sysUtility import getPaPyCode
import re

class Parser:
    res_dict_list=None#解析结果字典
    doc_type=""#html xml  json
    rules=None
    document=None
    parentDict={}
    def __init__(self,strDoc,doc_type="html",rules=[],parent_dict={}):
        #print "parser init ....."
        self.res_dict_list=[]
        if(len(strDoc)==0):
            msgPrint("invalid document string !")
            return -1
        self.doc_type=doc_type.lower()#参数标准化比较
        self.rules=rules
        if(self.doc_type.startswith("html")):
            self.doc_type="html"#参数标准化比较
            parser = etree.HTMLParser()
            self.document=html.document_fromstring(unicode(strDoc),parser)
        elif(self.doc_type.startswith("xml")):
            self.doc_type="xml"#参数标准化比较
            parser = etree.XMLParser()
            self.document=html.document_fromstring(unicode(strDoc),parser)
        elif(self.doc_type.startswith("json")):
            self.doc_type="json"#参数标准化比较
            self.document=json.loads()
        #继承数据项
        self.parentDict=parent_dict.copy()
    #清洗数据结果
    def cleanData(self,nodes):
        #xpath匹配不到数据的时候返回一个空格，不返回空字符串,空字符串会影响 and or语句的执行
        res=""
        if(isinstance(nodes,str)):
            return nodes
        for node in nodes:
            if(etree.iselement(node)):
                res=res+html.tostring(nodes[0], pretty_print=True, encoding='utf-8')
            else:
                t_res=len(node.strip())>0 and res+";"+node.strip() or res
                res=len(res.strip())>0 and t_res or t_res[1:]
        res=(len(res)!=0) and res or " "
        res=res.replace("\\","\\").replace("\'","\\'").replace('"','\\"')#避免存储时出错
        return str(res)
    #根据路径获取节点或者目标字符串
    def getPathValue(self,node,path):
        # if(path.startswith("=")):
        #     return node
        if(path.strip()==''):
            return ' '
        if(self.doc_type=='html' or self.doc_type=='xml'):
            res=node.xpath(path)
        else:
            res=eval("node"+path)
        return res
    #执行python代码，如果没有str_var参数，则直接执行python代码，目的为允许只有
    def getEvalValue(self,pycode,str_var=""):
        str_var=str_var.replace('\r','').replace('\n','').strip()
        if(str_var==""):
            return (pycode.find("%s")==-1) and eval(pycode) or " "
        else:
            return (pycode.find("%s")>-1) and eval(pycode.replace('%s',str_var)) or str_var
    #正常解析
    def parseNormal(self):
        res_dict=self.parentDict
        for rule_name in self.rules:
            if(not self.rules[rule_name].startswith("_list")):
                for tspath in self.rules[rule_name].split(";"):
                    spath,pycode=getPaPyCode(tspath)
                    if(rule_name.startswith("_")):
                        res_dict[rule_name]=self.getPathValue(self.document,spath)
                    elif(not spath.startswith("_list")):
                        sval=self.cleanData(self.getPathValue(self.document,spath))
                        stres=(pycode=="pass") and sval or self.getEvalValue(pycode,sval)
                        stres=len(stres.strip())>0 and ";"+stres or " "
                        t_flag=(rule_name in res_dict)and len(res_dict[rule_name].strip())>0
                        res_dict[rule_name]=t_flag and (res_dict[rule_name]+stres) or (stres[1:])
        return res_dict
    #解析文档
    def parseDocument(self):
        res_dict=self.parseNormal()
        #print res_dict["data_id"]
        if("_list" not in self.rules):
            self.res_dict_list.append(res_dict.copy())
            return
        #parse the item which depends on the list
        for node in res_dict["_list"]:
            t_res_dict=res_dict.copy()
            t_key_list=[]#临时键值集合
            for rule_name in self.rules:
                if(self.rules[rule_name].startswith("_list")):
                    for tspath in self.rules[rule_name].split(";"):
                        spath,pycode=getPaPyCode(tspath)
                        #如果依赖 _list 则从list节点中执行xpath
                        if(spath.startswith("_list")):
                            #spath需要移除前面的 '_list#'
                            sval=self.cleanData(self.getPathValue(node,spath[6:]))
                            #print sval,pycode
                            stres=(pycode=="pass") and sval or self.getEvalValue(pycode,sval)
                            stres=len(stres.strip())>0 and ";"+stres or " "
                            t_flag=(rule_name in t_key_list) and len(t_res_dict[rule_name].strip())>0
                            t_res_dict[rule_name]=t_flag and (t_res_dict[rule_name]+stres) or (stres[1:])
                            (rule_name in t_key_list) and t_key_list or t_key_list.append(rule_name)
            self.res_dict_list.append(t_res_dict)








