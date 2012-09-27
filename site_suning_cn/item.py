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

class spider_suning_item(object):
    
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
        page_deep = re.compile(r'<i id="pageTotal">(\d+)</i>',re.I|re.S|re.M)
        size = int(page_deep.findall(page)[0])

        _urls = [gen_page(url,p) for p in xrange(0,size)]
        for _u in _urls:
            yield self.generater_split_page,_u

    def generater_split_page(self, page, url):

        item_url = re.compile(r'http://www.suning.com/emall/prd_\d+_\d+_-\d+_\d+_.html',re.I|re.S|re.M)
        urls = item_url.findall(page)
        urls = set(urls)

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
        #print get_item_adv_model(page)
        store_shangping, store_adv = get_item_adv_model(page)
        store_thumb = extract(item_thumb,page,False)

        store_pingpai = ''
        #print extract(item_category_property,page,False)
        store_category,store_propperty = extract(item_category_property,page,False)

        store_price = extract(item_current_price,page)
        print store_price

        item_id = url.split('/')[-1].split('.')[0]

        #print store_thumb
        #print store_category
        #print item_id,store_category,store_price,store_thumb,store_model,store_adv

        data_record({'item_id':item_id,'brand':store_pingpai,'model':store_shangping,'title':store_title,'desc':store_desc,'adv':store_adv,'current_price':store_price,'item_url':url,'item_thumb':';'.join(store_thumb),'category':store_category,'property':store_propperty})
        IndexDB.insert(url)
        return None




        
def example():
    TSZ = spider_suning_item(['http://search.suning.com/emall/pcd.do?ci=20103'])
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
