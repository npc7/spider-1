# coding=utf-8
# author=spenly
# mail=i@spenly.com

import requests
import time
import urllib
import random
from logger import msg_print


def url_encode(words):
    """
    simple url encode
    :param words: words need to encode
    :return: string words after encode
    """
    return urllib.urlencode({"value": words})[6:]


def get_charset(headers):
    """
    get response encoding code by response header
    :param headers: response http header object
    :return: string encoding name
    """
    charset = "utf8"
    if "Content-Type" in headers:
        scs = str(headers["Content-Type"]).split(";")
        for s in scs:
            s = s.strip().lower().replace("-", '')
            if s.startswith("charset="):
                charset = s[8:]
                break
    return charset


def to_utf8_string(stext, charset="utf8"):
    """
    trans any string or unicode object to string with UTF8
    :param stext:
    :param charset: old encoding if you know
    :return: string with utf8
    """
    try:
        if isinstance(stext, unicode):
            stext = stext.encode("utf8")
        else:
            stext = unicode(stext, encoding=charset).encode("utf8")
        return stext
    except Exception:
        stext = unicode(stext, encoding="gbk", errors="ignore").encode("utf8")
    return stext


class HtmlUtility:
    def __init__(self, time_out=30, error_sleep=10):
        """
        init
        :param time_out: request timeout
        :param sleep:
        :param nsleep:
        :param nrange:
        """
        self.proxy = None
        self.session = requests.session()
        self.time_out = time_out
        self.error_sleep_time = error_sleep

    def set_proxy(self, ip, port, user="", pswd=""):
        """
        set proxy
        :param ip: 代理服务器IP
        :param port: 代理服务器端口
        :param user: 账户
        :param pswd: 密码
        :return:
        """
        if len(user) == 0:
            self.proxy = {"http": "http://%s:%s" % (ip, port)}
        else:
            self.proxy = {"https": "http://%s:%s@%s:%s" % (user, pswd, ip, port)}

    def clean_proxy(self):
        """
        clean proxy setting
        :return:
        """
        self.proxy = None

    def get(self, url, try_times=0, headers=None):
        """
        构造get请求
        :param url: 链接地址
        :param try_times: 已经重试次数, 如果请求失败, 自动尝试三次
        :param headers: 自定义请求头
        :return: 请求的内容
        """
        try:
            url = url.strip()
            msg_print("trying to request[GET]: " + url)
            r = self.session.get(url, timeout=self.time_out, headers=headers, proxies=self.proxy)
            re_text = r.content
            charset = get_charset(r.headers)
            re_text = to_utf8_string(re_text, charset)
            return re_text
        except Exception, e:
            time.sleep(self.error_sleep_time)
            msg_print(("request[GET] exception :", str(e)))
            try_times += 1
            if try_times < 3:
                msg_print("retrying ...")
                return self.get(url, try_times, headers)
            else:
                return ''

    def post(self, url, post, try_times=0, headers=None):
        """
        构造post请求
        :param url: 链接地址
        :param post: post 数据, dict对象
        :param try_times: 已经重试次数, 如果请求失败, 自动尝试三次
        :param headers: 自定义请求头
        :return: 请求的内容
        """
        try:
            url = url.strip()
            msg_print("Request [ POST ]: " + url)
            r = self.session.post(url, data=post, headers=headers, timeout=self.time_out, proxies=self.proxy)
            re_text = r.content
            charset = get_charset(r.headers)
            re_text = to_utf8_string(re_text, charset)
            return re_text
        except Exception, e:
            time.sleep(self.error_sleep_time)
            msg_print(("Request [POST] exception :", str(e)))
            try_times += 1
            if try_times < 3:
                msg_print("Retrying ...")
                return self.post(url, post, try_times, headers)
            else:
                return ''

    def dowdload(self, url, post=None, try_times=0):
        """
        构造文件下载请求
        :param url: 请求链接
        :param post: GET 方式为 None, Post 为 POST 数据, 默认为 None (GET)
        :param try_times: 已经重试次数, 如果请求失败, 自动尝试三次
        :return: 二进制对象
        """
        try:
            msg_print("Download [ %s ]:" % (post and "POST" or "GET") + url)
            if (post):
                res = self.session.post(url, data=post).content
            else:
                res = self.session.get(url, timeout=self.time_out).content
            return res
        except Exception, e:
            time.sleep(self.error_sleep_time)
            msg_print(("Download exception :", str(e)))
            try_times += 1
            if try_times < 3:
                msg_print("Retrying ...")
                return self.dowdload(url, post, try_times)
            else:
                return None
