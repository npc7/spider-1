#encoding=utf8
'''
Created on 2014-9-10
@author: jzx
'''
from logger import msgPrint
from docParser import Parser
from htmlUtility import HtmlUtility
from mysqlUtility import MysqlUtility
from sysUtility import readConf
from sysUtility import getLocalIP
from sysUtility import getPID
from sysUtility import getValue
import time
import re

class Controller:
    mysql=None
    spider_name=None
    feed_list=None
    rule_dict=None
    start_url_list=None
    is_init_success=True
    sleep_time=0
    __spider_name=""
    __spider_level=""
    __spider_site=""
    __spider_tag=""

    def __init__(self,spider_name):
        if(len(spider_name.split("_"))!=4):
            msgPrint("initialization error,please check spider name !")
            self.is_init_success=False
            return
        self.spider_name=spider_name
        ss=spider_name.split("_")
        self.__spider_name=ss[0]
        self.__spider_level=ss[1]
        self.__spider_site=ss[2]
        self.__spider_tag=ss[3]
        conf_lines=readConf()
        for line in conf_lines:
            line=line.lower()#转换成小写
            if(line.startswith("mysql:")):
                lts=getValue(line.replace("\n","")).split(" ")
                try:
                    msgPrint("mysql://%s/%s  %s@%s"%(lts[0],lts[1],lts[2],lts[3]))
                    self.mysql=MysqlUtility(ip=lts[0],db=lts[1],user=lts[2],pswd=lts[3])
                except Exception,ex:
                    msgPrint(str(ex))
                    self.mysql=None
            elif(line.startswith("sleep:")):
                value=getValue(line.replace("\n",""))
                self.sleep_time=(value==None) and None or int(value)
        if(self.mysql==None):
            msgPrint("initialization error,please check config file !")
            self.is_init_success=False
    #获取采集种子
    def get_feeds(self):
        self.feed_list=[]
        rows=self.mysql.select_record("select data_id,url,paras,table_from,table_save,page_ttype,page_dtype,py_url,py_html,store from feed where spider_name='%s'"%self.spider_name)
        for row in rows:
            feed={}
            feed["data_id"]=(row[0]==None) and " " or str(row[0])
            feed["url"]=(row[1]==None) and " " or str(row[1])
            feed["paras"]=(row[2]==None) and " " or str(row[2])
            feed["table_from"]=(row[3]==None) and " " or str(row[3])
            feed["table_save"]=(row[4]==None) and " " or str(row[4])
            feed["page_ttype"]=str(row[5]).lower()#统一转换成小写
            feed["page_dtype"]=str(row[6]).lower()#统一转换成小写
            feed["py_url"]=(row[7]==None) and " " or str(row[7])#含有python代码，不能进行大小写转换
            feed["py_html"]=(row[8]==None) and " " or str(row[8])#含有python代码，不能进行大小写转换
            feed["store"]=str(row[9]).lower()
            self.feed_list.append(feed.copy())
        if(len(self.feed_list)==0):
            msgPrint("can't match any feeds by spider name :%s"%self.spider_name)
            self.feed_list=None
    #采集种子转换成起始链接的扩展
    def get_task_url(self,feed):
        table=feed["table_from"]
        swhere=feed["url"]
        if(swhere.startswith("http")):
            return
        if(len(swhere.strip())==0):
            swhere="1=1"
        spid=getLocalIP()+":"+getPID()
        #未出售和未消失的
        #and (miss_info is NULL and sale_info is NULL or update_time<DATE_SUB(NOW(),INTERVAL 5 DAY))
        strSql="update %s set is_crawl=0,pid='%s' where (site='%s' and  tag='%s') %s LIMIT 5"
        strSql=strSql%(table,spid,self.__spider_site,self.__spider_tag,swhere)
        #print strSql
        self.mysql.update_record(strSql)#先申请任务
        strSql="SELECT data_id,url from %s where is_crawl=0 and pid='%s' and site='%s' and  tag='%s'"%(table,spid,self.__spider_site,self.__spider_tag)
        results=self.mysql.select_record(strSql)
        if(results==None):
            return
        for row in results:
            tmp_url=feed.copy()
            tmp_url["data_id"]=row[0]
            tmp_url["url"]=row[1]
            self.start_url_list.append(tmp_url)
    #把采集种子转换成起始链接
    def build_feed(self):
        self.start_url_list=[]
        for feed in self.feed_list:
            turl=feed["url"]
            data_id=feed["data_id"]
            paras=feed["paras"].split(";")
            #参数处理
            # if(len(paras)!=3):#限制最多两个参数  {page} {max} {type}
            #     msgPrint( ("can't format the feed,only need 3 paras ! feed->data_id:",data_id))
            #     continue #处理下一行数据
            for para in paras:# {page}:0;{type}:1|2|3  分别处理每组参数
                if(para.strip()==''):
                    continue
                if(para.startswith("{page}")):#页码形式
                    tps=para.split(":")
                    if(len(tps)!=2):#格式错误
                        msgPrint(( "wrong page format :",para," data_id:",data_id))
                        break
                    feed["{page}"]=tps[1]
                elif(para.startswith("{max}")):#最大页码数
                    tps=para.split(":")
                    if(len(tps)!=2):#格式错误
                        msgPrint(( "wrong page format :",para," data_id:",data_id))
                        break
                    feed["{max}"]=tps[1]
            para_flag=False
            for para in paras:# {page}:0;{type}:1|2|3  分别处理每组参数
                if(not para.strip()=='' and not para.startswith("{page}")and not para.startswith("{max}")):
                    tps=para.split(":")
                    if(len(tps)!=2):#格式错误
                        msgPrint(("wrong parameter format :",para," data_id:",data_id))
                        break
                    for pv in tps[1].split("|"):
                        para_flag=True
                        feed["url"]=turl.replace(tps[0],pv)
                        self.start_url_list.append(feed.copy())
            if(turl.startswith("http")and not para_flag):#仅有 {max} 和 {page} 两个参数
                self.start_url_list.append(feed)
            if(not turl.startswith("http")):
                self.get_task_url(feed)
            #check start_url_list
        if(len(self.start_url_list)==0):
            msgPrint("can't build urls from feed !")
            self.start_url_list=None
    #获取采集规则
    def get_rules(self,rule_name):
        if(self.rule_dict==None):
            self.rule_dict={}
        all_keys=[]#临时键列表
        # spider_name 默认为 rule_name + tag
        #这么做是为了实现同一套规则的复用
        rows=self.mysql.select_record("SELECT db_field,path from rules where rule_name='%s'"%rule_name)
        for row in rows:
        #如果存在则添加
        #这样做是为了实现，同一个规则下可以多个规则表达式
            if(row[0] not in all_keys):#保证rule优先级高的可以覆盖掉优先级低的
                self.rule_dict[row[0]] = row[1]
                all_keys.append(row[0])
            else:#存在则追加
                self.rule_dict[row[0]]=self.rule_dict[row[0]]+";"+row[1]
        if(len(self.rule_dict)==0):
            msgPrint("can't match any rules by spider name :%s"%self.spider_name)
            self.rule_dict=None
    #根据存储参数进行存储
    def store_dict(self,url_item,dict):
        store_type,store_mode=url_item["store"].split(":")
        if(store_type=="insert"):
            self.mysql.insert_dict(dict,url_item["table_save"],store_mode)
        else:
            self.mysql.update_dict(dict,url_item["table_save"],store_mode)
    #获取结果集中是否还有下一页
    def get_is_next(self,res_dict_list):
        if(len(res_dict_list)>0 and "_is_next" in res_dict_list[0]):
            is_next=len(res_dict_list[0]["_is_next"])>0
        else:
            is_next=False
        return is_next
    #采集流程控制
    def crawl_control(self,url_item):
        htmlutt=HtmlUtility()
        is_page_no=False#页码标识
        if("{page}" in url_item):# 多页
            is_page_no=True
            page_no,page_size=url_item["{page}"].split("*")
        is_next=True
        max_page=("{max}" in url_item) and  int(url_item["{max}"]) or 9999
        while(is_next):
            page_index=is_page_no and int(page_no)*int(page_size) or 0
            url=is_page_no and url_item["url"].replace("{page}",str(page_index)) or url_item["url"]
            #对url进行处理
            url=(len(url_item["py_url"].strip())==0) and url or eval(url_item["py_url"]%url)
            parent_dict={}
            if(url_item["store"].startswith("insert")):
                parent_dict["ref_url"]=url
                parent_dict["site"]=self.__spider_site
                parent_dict["tag"]=self.__spider_tag
            parent_dict["data_id"]=url_item["data_id"]
            str_html=htmlutt.getPageSource(url,isMob=(url_item["page_ttype"].startswith("m")))
            if(len(str_html.strip())>0):#获取成功
                #对获取到的html进行处理
                str_html=(len(url_item["py_html"].strip())==0) and str_html or eval(url_item["py_html"]%str_html)
                doc_parser=Parser(strDoc=str_html,doc_type=url_item["page_dtype"],rules=self.rule_dict,parent_dict=parent_dict)
                doc_parser.parseDocument()
                for res_dict in doc_parser.res_dict_list:
                    self.store_dict(url_item,res_dict)
                is_next=is_page_no and self.get_is_next(doc_parser.res_dict_list)
            else:
                msgPrint("can't get the page source !")
                self.mysql.update_get_page_fail(url_item["data_id"],url_item["table_from"])
                is_next=False# 没有下一页
            if(is_next):
                page_no =str(int(page_no) + 1)
            if(is_next and is_page_no and int(page_no)>max_page):
                is_next=False
            time.sleep(self.sleep_time)
    #info模式时，从数据库筛选任务链接
    def check_task_url(self):
        if(len(self.start_url_list)>0):
            return
        for feed in self.feed_list:
            self.get_task_url(feed)
    #采集
    def start_crawl(self):
        self.get_feeds()
        rule_name="%s_%s_%s"%(self.__spider_name,self.__spider_level,self.__spider_site)
        self.get_rules(rule_name)#获取通用的rule
        self.get_rules(self.spider_name)#获取优先级更改的spider专用rule
        if(self.feed_list==None or self.rule_dict==None):
            return
        self.build_feed()
        if(self.start_url_list==None):
            return
        is_cycle=len(self.start_url_list)>0
        while(is_cycle):
            url_item=self.start_url_list.pop(0)
            self.crawl_control(url_item)
            self.check_task_url()
            is_cycle=(len(self.start_url_list)>0)









