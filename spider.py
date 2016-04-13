#coding=utf-8
'''
Created on 2013-11-21
@author: jzx
'''
import sys
from controller import Controller
from logger import msgPrint

reload(sys)
sys.setdefaultencoding('utf8')

spider_name=""
# get start parameter
try:
    spider_name=str(sys.argv[1])#parameter : spider name  eg:spider_page_58_sh
except:
    print "start parameter error ,will end !"
    exit(-1)
# do local inition
msgPrint(spider_name+' start !')
controller=Controller(spider_name)
if(controller.is_init_success):
    controller.start_crawl()

msgPrint(spider_name+' end !')



