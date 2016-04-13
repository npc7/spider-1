#!/usr/bin/python
#encoding=utf8
'''
本文件的名字需要包含 spider.py 在使用stop参数时才能把自己也结束掉
'''
import sys
import os
import time
import signal



#开始启动监测
def start():
    os.system("cd /home/ubuntu/new_spider")
    while(1):
        #早七点和晚七点
        if(int(time.strftime("%H"))%12==7):
            os.system("nohup python manager.py spider_list >/dev/null &")
            time.sleep(600)# 10 min
            os.system("nohup python manager.py spider_info >/dev/null &")
            time.sleep(600)# 10 min
            os.system("nohup python manager.py check_info >/dev/null &")
            time.sleep(2400)
        else:
            time.sleep(3600)
    #获取当前路径
    #path = "/root/albb/"

    # while(1):
    #     processInfo = os.popen("ps -ef | grep 'python albb_com.py' | grep -v grep").readlines()
    #     processNum = len(processInfo)
    #     if(processNum<Max_process):
    #         os.system('cd '+path)
    #         os.system('nohup ./run_albb_com.sh >/dev/null &')
    #         time.sleep(2)
    #         print "Gen new process."
    #     else:
    #         time.sleep(5)


#杀掉所有运行抓取数据的进程
def stopChicd():
    processInfo = os.popen("ps -ef|grep 'python spider.py' |grep -v grep|awk '{print $2}'").readlines()
    for pid in processInfo:
        os.kill(int(pid),signal.SIGKILL)

#杀掉抓取进程和其他监测进程
def stopAll():
    stopChicd()


try:
    fun = sys.argv[1]
except Exception:
    fun = ''
if(fun == 'start'):
    start()
if(fun == 'stop'):
    stopAll()
if(fun == 'restart'):
    stopAll()
    time.sleep(1)
    start()



