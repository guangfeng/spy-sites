#!/usr/bin/env python
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

class spider_360_item(object):
    
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
        x = re.compile(r'1/(\d+)</span>',re.I|re.M|re.S)
        _size = x.findall(page)
        page_size = int(_size[0])

        _urls = [url[0:-5]+"-0-0-0-0-0-0-0-1-1-%d.html"%p for p in xrange(1,page_size + 1)]
        for _u in _urls:
            yield self.generater_split_page,_u

    def generater_split_page(self, page, url):
#        r1 = re.compile(r'http://www.360buy.com/product/\d+.html',re.I|re.M|re.S)
#        urls = r1.findall(page)
        urls = extract(item_url,page,False)
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
        store_desc = extract(item_store_desc,page)
        store_adv = extract(item_store_ad,page)
        store_thumb = extract(item_thumb,page,False)

        c = re.compile(r'href="http://www.360buy.com/products/\d+-\d+-\d+.html">(.*?)</a>',re.I|re.M|re.S)
        _c = c.findall(page)
        store_categorys = _c

        #store_categorys = extract(item_category,page,False)
        store_pingpai = extract(item_pingpai,page)
        store_shangping = extract(item_shangping(url),page)
        item_id = url.split('/')[-1].split('.')[0]
        #item_image = item_price_image(item_id)

        #print item_id,store_title,item_image,store_shangping,store_pingpai,store_desc,store_adv,url,item_category
        #print store_category
        if not store_categorys or len(store_categorys) == 1:
            store_category = item_property = ''
        elif len(store_categorys) < 3:
            store_category = store_categorys[1]
            item_property = ''
        else:
            store_category = store_categorys[1]
            item_property = store_categorys[2]

        data_record({'item_id':item_id,'brand':store_pingpai,'model':store_shangping,'title':store_title,'desc':store_desc,'adv':store_adv,'current_price':0,'item_url':url,'item_thumb':';'.join(store_thumb),'category':store_category,'property':item_property})
        IndexDB.insert(url)
        return None




        
def example():
    TSZ = spider_360_item('http://www.360buy.com/products/652-828-840.html')
    #fetcher = Fetch(cache = 'cache',char = 'gb18030')
    fetcher = NoCacheFetch(char ='gb18030', proxy = '127.0.0.1:8090')
    spider = Rolling(fetcher,TSZ.generater_item_index())
    spider_runner = GSpider(spider, workers_count=5)
    spider_runner.start()

def Graphs():
    import urllib2
    root = urllib2.urlopen('http://www.360buy.com/digital.html').read()
    pattern = re.compile(r'http://www.360buy.com/products/\d+-\d+-[1-9]+.html',re.I|re.S|re.M)
    children = pattern.findall(root)
    return children

print set(Graphs())