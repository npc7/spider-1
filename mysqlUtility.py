#coding=utf-8
'''
Created on 2013-11-21
@author: jzx
'''
import MySQLdb
import time
from logger import msgPrint


class MysqlUtility:
    conn=None
    cursor=None
    ############# basic function ################
    def __init__(self,ip,db,user,pswd):
        self.conn=MySQLdb.connect(host=ip,user=user,passwd=pswd,db=db,charset='utf8')
        self.cursor=self.conn.cursor()
    #delete
    def delete_record(self,sql):
        try:
            res=self.cursor.execute(sql)
            self.conn.commit()
            return res
        except Exception,ex:
            print ex
    #update
    def update_record(self,sql):
        try:
            res=self.cursor.execute(sql)
            self.conn.commit()
            return res
        except Exception,ex:
            print ex
            return 0
    #insert
    def insert_record(self,sql):
        try:
            res=self.cursor.execute(sql)
            self.conn.commit()
            return res
        except Exception ,ex:
            print ex
            return 0
    #select
    def select_record(self,sql):
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Exception,ex:
            print ex
            return None

    ############  advance function  ##########
    def insert_dict(self,dict,table="result",mode="his"):
        #print "dict",dict
        sfield=""
        svalue=""
        now_time=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
        supdate="update_time='%s',"%now_time
        for key in dict:
            if(key.startswith("_")):#仅程序里需要使用的键值对
                continue
            key=(key.endswith("_")) and key[:-1] or key #需要传递的键值对
            sfield=sfield+key+","
            svalue=svalue+"'"+ dict[key] +"',"
            supdate=supdate+"%s='%s',"%(key,dict[key])
        if(len(sfield)==0 or len(svalue)==0):
            msgPrint("result dict has no key-value ! save canceled !")
            return
        #默认为his模式（需要历史数据）
        #存在则更新下update_time,表示数据还在，不存在则插入
        strSql="insert ignore into  %s (%s)values (%s) ON DUPLICATE KEY UPDATE %s"%(table,sfield[:-1],svalue[:-1],supdate[:-1])
        #如果为syn（实时同步模式）
        if(mode=="syn"):
            strSql="REPLACE INTO %s (%s) values (%s)"%(table,sfield[:-1],svalue[:-1])
        #print strSql
        ires=self.insert_record(strSql)
        msgPrint(ires>0 and "insert or update time success !" or ("insert or update failed !"))

    def update_dict(self,dict,table="result",mode="his"):
        now_time=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
        setStr="is_crawl=1,update_time='%s',"%now_time
        whereStr="data_id='%s'"%dict.pop("data_id")
        for key in dict:
            #如果匹配到再更新 无信息则以原值为准
            if((mode=="his" and len(str(dict[key]).strip())>0) or mode=="syn"):
                setStr=setStr+"%s='%s',"%(key,dict[key])
        strSql="update %s set %s where %s"%(table,setStr[:-1],whereStr)
        #print str(strSql)
        ires=self.insert_record(strSql)
        msgPrint(ires>0 and "update info success !" or ("update failed !"))

    def update_get_page_fail(self,data_id,table="result"):
        strSql="update %s set is_crawl=-1 where data_id='%s'"%(table,data_id)
        self.update_record(strSql)
