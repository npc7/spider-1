#encoding=utf8
import os
import sys
from sysUtility import readConf
from sysUtility import getValue
from mysqlUtility import MysqlUtility
from logger import msgPrint
import time

reload(sys)
sys.setdefaultencoding('utf8')
scmd="%s_%s_%s"



def crawl_site(scmd):
    cmd="nohup python spider.py "+scmd+">/dev/null &"
    print cmd
    #print os.getpid()
    os.system(cmd)

if __name__=="__main__":
    spider_name=""
    try:
        spider_name=sys.argv[1]
    except Exception,ex:
        print 'invalid parameters, will exit .'
        exit(0)
    conf_lines=readConf()
    mysql=None
    for line in conf_lines:
        line=line.lower()#转换成小写
        if(line.startswith("mysql:")):
            lts=getValue(line.replace("\n","")).split(" ")
            try:
                msgPrint("mysql://%s/%s  %s@%s"%(lts[0],lts[1],lts[2],lts[3]))
                mysql=MysqlUtility(ip=lts[0],db=lts[1],user=lts[2],pswd=lts[3])
            except Exception,ex:
                msgPrint(str(ex))
                mysql=None
    if(mysql==None):
        msgPrint("initialization error,please check config file !")
        exit(0)
    strsql="select spider_name from feed where spider_name like '%"+"%s"%spider_name+"%'"
    for row in mysql.select_record(strsql):
        crawl_site(str(row[0]))

