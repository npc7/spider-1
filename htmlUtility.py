#coding=utf-8
'''
Created on 2014-08-29
@author: jzx
'''
import requests
import time
from logger import msgPrint

class HtmlUtility:
    def __init__(self):
        pass

    proxy=None
    #{"https":"http://sunny:hsjdbdk783@107.155.94.43:8080"}
    #{"http":"http://107.155.94.43:8080"}
    #headers = {'Accept-Language':'en-US,zh-CN;q=0.5','User-Agent':'Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16'}

    def setProxy(self,ip,port,user="",pswd=""):
        if(len(user)==0):
            self.proxy={"http":"http://%s:%s"%(ip,port)}
        else:
            self.proxy={"https":"http://%s:%s@%s:%s"%(user,pswd,ip,port)}

    def resetProxy(self):
        self.proxy=None
    #获取页面内容
    def getPageSource(self,url,try_times=0,isMob=False):
        try:
            url=url.strip()
            msgPrint("trying to get : "+url)
            msgPrint(("proxy:",self.proxy,"; Terminal type:",isMob and "Mobile" or "PC"))
            sua='Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)'
            #是否模拟移动端
            if(isMob):
                sua='Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16'
            headers = {'Accept-Language':'	zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3','Accept':'text/html,xhtml+xml','User-Agent':sua}
            r = requests.get(url,headers=headers,timeout=60,proxies=self.proxy)
            #reText =r.content# r.text.encode('utf8')
            reText =(r.content)
            charset="utf8"
            if("Content-Type" in r.headers):
                strsContentType=str(r.headers["Content-Type"]).split(";")
                for s in strsContentType:
                    s=s.strip().lower().replace("-",'')
                    if(s.startswith("charset=")):
                        charset=s[8:]
            #reText =(charset!='utf8') and reText.decode(charset).encode("utf8") or reText
            try:
                reText =unicode(reText,encoding=charset).encode("utf8")
            except Exception:
                reText =unicode(reText,encoding="gbk",errors="ignore").encode("utf8")
            return reText
        except Exception,e:
            time.sleep(2)
            msgPrint(("get page source exception :",str(e)))
            try_times=try_times+1
            if(try_times<3):
                return self.getPageSource(url,try_times)
            else:
                return ''