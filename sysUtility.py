#coding=utf-8
'''
Created on 2014-08-29
@author: jzx
'''
import re
import socket
import os

def replace(regex,tostr,str):
    patern=re.compile(regex)
    print patern.subn(tostr,str)[0]

def getLocalIP():
    return str(socket.gethostbyname(socket.gethostname()))

def getPID():
    return str(os.getpid())

#解析，分解path和python代码
def getPaPyCode(strPath):
    sxpath=(strPath.find("{py:")<0) and strPath or strPath[:strPath.find("{py:")]
    pycode=(strPath.find("{py:")<0) and "pass" or (strPath[strPath.find("{py:")+4:-1])
    pycode=len(pycode)==0 and "pass" or pycode
    return sxpath,pycode
#读取系统配置文件
def readConf():
    conf=open("conf.txt")
    lines=conf.readlines()
    conf.close()
    for line in lines:
        if(line.startswith("#")):
            lines.remove(line)
    return lines

def getValue(key_value):
    ss=key_value.split(":")
    if(len(ss)==2):
        return ss[1].strip()
    else:
        return None
