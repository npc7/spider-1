# /usr/bin/python
# encoding=utf8
# author=spenly
# mail=i@spenly.com

from html_utility import HtmlUtility
from doc_parser import doc_parser, extract_data

htu = HtmlUtility()

out_cat_file = "data/mybb_cat.csv"


def parse_task(url):
    wf = open(out_cat_file, "w")
    sou_page = htu.get(url)
    doc = doc_parser(sou_page)
    cns = doc.xpath("//div[@class='dls']/dl//div[@class='colum']")
    for idx in range(0, len(cns)):
        cat_name = extract_data(cns[idx].xpath("./h3/text()"))
        for sub_cat in cns[idx].xpath(".//p/a"):
            sub_cat_name = extract_data(sub_cat.xpath("./text()"))
            sub_cat_url = extract_data(sub_cat.xpath("./@href"))
            print(" , ".join([cat_name, sub_cat_name, sub_cat_url]))
            wf.write(",".join([cat_name, sub_cat_name, sub_cat_url]) + "\n")
    wf.close()


if __name__ == "__main__":
    parse_task("http://www.mia.com/")
