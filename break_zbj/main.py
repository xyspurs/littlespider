#!/usr/bin/env python

# 爬取猪八戒网站
import copy
import requests
import lxml
from lxml import etree
import time
import random


area_code = {"广州": "3493", "深圳": "3510", "佛山": "3498"}

catalog_code = {
                "软件开发": "rjkf", 
                "APP开发": "ydyykf", 
                "IT解决方案": "itfangan",
                "软件/SAAS": "saas",
                "微信开发": "wxptkf",
                "技术服务": "jsfwzbj",
                "研究开发": "yjkfzbj"
                }

first_page_url_template="http://www.zbj.com/{catalog}/pd{area}.html"
url_template="http://www.zbj.com/{catalog}/pd{area}k{pagenum}.html"

headers={
        "Host":"www.zbj.com",
        "Connection":"keep-alive",
	"Pragma":"no-cache",
	"Cache-Control":"no-cache",
	"Upgrade-Insecure-Requests":"1",
	"User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
	"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
	"Accept-Encoding": "gzip, deflate",
	"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7"
        }

def transform_headers(headers, **kw):
    tmp = copy.deepcopy(headers)
    tmp.update(kw)
    return tmp

ucenter_headers=headers.update({"Host": "ucenter.zbj.com"})
shop_headers=headers.update({"Host": "shop.zbj.com"})

def get_total_page_num(text):
    """  从html中找出总页数"""
    dom = etree.HTML(text)
    spans = dom.xpath("//span[@class='ui-minipaging-pagenum']")
    assert(len(spans) == 1)
    span = spans[0]
    pagenum_list = span.xpath("string(.)").split("/")
    assert(len(pagenum_list) == 2)
    pagenum = pagenum_list[1].strip()
    return int(pagenum)


def get_child_urls(text):
    """ 从html中找到所有的子链接, 返回列表"""
    dom = etree.HTML(text)
    hrefs = dom.xpath("//div[@class='service-provider-wrap j-service-provider-wrap ']/div//a[@class='shop-name text-overflow']/@href")
    return ["http:"+href for href in hrefs]


def aggregate_url(catalog, area, size=40):
    """ 根据不同区域，不同类别，找到相似的一类url地址集合 
        catalog: 行业分类代码 area:  地区代码 """
    first_page_url = first_page_url_template.format(catalog=catalog, area=area)
    rsp = requests.get(first_page_url, headers=headers)
    pagenum = get_total_page_num(rsp.text)
    url_cluster = set()
    urls = get_child_urls(rsp.text)  # 第一页也要获取其所有子链接
    url_cluster.update(urls)
    #print(url_cluster)
    for i in range(1, pagenum):
        pagenum_suffix = i*size
        url = url_template.format(catalog=catalog, area=area, pagenum=pagenum_suffix) 
        rsp = requests.get(url, headers=headers)
        time.sleep(random.uniform(2.0,4.0)) # 避免访问过于频繁
        urls = get_child_urls(rsp.text)
        url_cluster.update(urls)
        #print(url_cluster)
    return url_cluster

def transform_url(url):
    """ 转换url，让其变成档案首页的url"""
    """ url示例: http://shop.zbj.com/17054627/ """
    assert isinstance(url, str)
    salerinfo_url=url+"salerinfo.html"
    spec_headers=transform_headers(headers, Host="shop.zbj.com")
    s = requests.session()
    s.headers.update(spec_headers)
    print(s.headers)
    rsp = s.get(salerinfo_url)
    dom = etree.HTML(rsp.text)
    hrefs = dom.xpath("//iframe[contains(@src, 'ucenter.zbj.com/rencai')]/@src")
    hrefs_length = len(hrefs)
    if hrefs_length >= 1:
        url_type = "ucenter"
        target_url = "http:"+hrefs[0]
    else:
        url_type = "tianpeng"
        target_url = salerinfo_url
    
    return target_url, url_type

def extract_info(page, url_type="ucenter"):
    """ 提取企业信息，包括 企业名，企业地址，企业自我介绍"""

def process_url(url):
    url, url_type = transform_url(url)
    assert url_type in ("tianpeng", "ucenter")
    if url_type == "tianpeng":
        spec_headers=transform_headers(headers, Host="shop.zbj.com")
    else:
        spec_headers=transform_headers(headers, Host="ucenter.zbj.com")
    rsp = requests.get(url, headers=spec_headers)
    company_info = extract_info(rsp.text, url_type)
    return company_info
    pass


if __name__ == "__main__":
    #rsp = requests.get("http://www.zbj.com/rjkf/pd3498.html", headers=headers)
    #pagenum = get_total_page_num(rsp.text)
    #urls = get_child_urls(rsp.text)
    ##print(urls)
    #result = aggregate_url(catalog_code["软件开发"],area_code["广州"])
    #print(result)
    print(transform_url("http://shop.zbj.com/17054627/"))
    pass
