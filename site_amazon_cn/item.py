#!/usr/bin/env python
# encoding: utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os.path as path
from spy import *
from rule import *
import re
from record import *
from multiprocessing import Pool
from toolkit import Index

IndexDB = toolkit.Index('task_url_list.db')

class spider_amazon_item(object):
    
    def __init__(self, start_urls = '', category = '', page_deep = 5):
        self.start_urls = start_urls
        self.category = category
        self.page_deep = page_deep

    def generater_item_index(self):
        for i in self.start_urls:
            if IndexDB.has(i):
                continue
            else:
                yield self.parser_item_index,i

    def parser_item_index(self, page, url):
        count = re.compile(r'1-(\d+)条',re.I|re.S|re.M)
        total = re.compile(r'共(\d+)条',re.I|re.S|re.M)
        page_ct = count.findall(page)[0]
        page_ta = total.findall(page)[0]
        page_deep = int(page_ta) / int(page_ct) + 1
        


        _urls = [gen_page(url,p) for p in xrange(1,page_deep + 1)]
        for _u in _urls:
            yield self.generater_split_page,_u

    def generater_split_page(self, page, url):

        reg_item = re.compile(r'/product-reviews/(.*?)/',re.I|re.M|re.S)
        urls = reg_item.findall(page)
        urls = set(urls)
        urls = ["http://www.amazon.cn/dp/%s"%it for it in urls]

        for _u in urls:
            if IndexDB.has(_u):
                continue
            else:
                yield self.parser_item_page,_u
    
    def parser_item_page(self, page, url):
        if IndexDB.has(url):
            return None

        store_title = extract(item_store_title,page)
        store_desc = ''
        store_adv = extract(item_store_ad,page)
        store_thumb = get_item_images(page)

        store_pingpai = extract(item_pingpai,page)
        store_shangping,store_category = get_shangping_fenlei(store_title)

        store_price = extract(item_current_price,page)
        print store_price

        if store_price:
            store_price = store_price.split(' ')[-1]
            store_price = store_price.replace(',','')
        else:
            store_price = 0

        item_id = url.split('/')[-1]

        #print store_thumb
        #print store_category
        item_property = ''

        data_record({'item_id':item_id,'brand':store_pingpai,'model':store_shangping,'title':store_title,'desc':store_desc,'adv':store_adv,'current_price':store_price,'item_url':url,'item_thumb':store_thumb,'category':store_category,'property':item_property})
        IndexDB.insert(url)
        return None




        
def example():
    TSZ = spider_amazon_item(['http://www.amazon.cn/s/ref=sv_cps_10?ie=UTF8&page=1&rh=n%3A665189051'])
    #fetcher = Fetch(cache = 'cache',char = 'gb18030')
    fetcher = NoCacheFetch(proxy = '127.0.0.1:8090')
    spider = Rolling(fetcher,TSZ.generater_item_index())
    spider_runner = GSpider(spider, workers_count=5)
    spider_runner.start()

def Graphs():
    import urllib2
    root = urllib2.urlopen('http://www.360buy.com/digital.html').read()
    pattern = re.compile(r'http://www.360buy.com/products/\d+-\d+-[1-9]+.html',re.I|re.S|re.M)
    children = pattern.findall(root)
    return children
