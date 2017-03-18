# encoding=utf8
# author=spenly
# mail=i@spenly.com

from lxml import etree, html
from html_utility import msg_print


def doc_parser(str_doc, doc_type="html"):
    """
    字符串格式化为 document 对象
    :param str_doc: 文本对象
    :param doc_type: document 对象类型 html,xml,json
    :return: html 和 xml返回 etree 的 document 对象, json 返回json 对象
    """
    if len(str_doc) == 0:
        msg_print("invalid document string !")
        return None
    doc_type = doc_type.lower().strip()
    document = None
    if doc_type == "html":
        parser = etree.HTMLParser()
        document = html.document_fromstring(str_doc.decode("utf8", ), parser)
    elif doc_type == "xml":
        parser = etree.XMLParser()
        document = html.document_fromstring(str_doc.decode("utf8"), parser)
    elif doc_type == "json":
        try:
            document = eval(str_doc, type('Dummy', (dict,), dict(__getitem__=lambda s, n: n))())
        except Exception, ex:
            msg_print("warning:> not regular json format !")
            msg_print(str(ex))
    return document


def extract_data(nodes, stype="a"):
    """
    get data from xpath nodes object
    :param nodes: xpath 筛选后的对象, 可能是 node, 也可能是 str
    :param stype: 筛选类型 'a' （all）筛选所有的值, 'f' (first)只筛选nodes中第一个node的值
    :return: 筛选后的结果
    """
    res = ""
    if isinstance(nodes, str):
        return nodes
    if isinstance(nodes, unicode):
        return nodes.encode("utf8")
    if isinstance(nodes, list) and len(nodes) > 0 and stype == "f":
        return extract_data(nodes[0])
    for node in nodes:
        if etree.iselement(node):
            res = res + html.tostring(node, pretty_print=True, encoding='unicode')
        else:
            t_res = len(node.strip()) > 0 and res + ";" + node.strip() or res
            res = len(res.strip()) > 0 and t_res or t_res[1:]
    res = res and res or " "
    return res.encode("utf8")
