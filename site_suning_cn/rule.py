#!/usr/bin/env python
# encoding: utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re

#page_deep = re.compile(r'<div class=\'pagin pagin-m\'>\s*<span class=\'text\'>1/(.*?)</span>',re.I|re.M|re.S)
page_every = re.compile(r'1-(\d+)条',re.I|re.S|re.M)
page_total = re.compile(r'共(\d+)条',re.I|re.S|re.M)


item_brand_model = re.compile(r'<ul id="i-detail">\s*<li title=".*?">商品名称：(.*?)</li>\s*<li>生产厂家：<a target="_blank" href=".*?">(.*?)</a></li>.*?</ul>',re.I|re.M|re.S)

item_store_title = re.compile(r'<title>(.*?)</title>',re.I|re.S|re.M)

item_store_desc = re.compile(r'<meta name="description" content="(.*?)"\s*/>',re.I|re.S|re.M)

item_store_ad = re.compile(r'<span id="btAsinTitle">(.*?)</span>',re.I|re.M|re.S)

#item_url = re.compile(r'"http://www.amazon.cn/product-reviews/(.*?)"\s*>',re.I|re.M|re.S)

item_thumb = re.compile(r'http://image\d+.suning.cn/content/catentries/\d+/\d+/fullimage/\d+_\d+.jpg',re.I|re.S|re.M)

item_category = re.compile(r'href="http://www.360buy.com/products/\d+-\d+-\d+.html">(.*?)</a>',re.I|re.M|re.S)

item_pingpai = re.compile(r'品牌:(.*?),',re.I|re.M|re.S)

item_current_price = re.compile(r'currPrice=(.*?)&isLogin=no',re.I|re.S|re.M)

item_category_property = re.compile(r'<a class="searchCity" href=".*?" title="(.*?)">',re.I|re.S|re.M)

item_adv = re.compile(r'<div class="pro_title pro_title_icon">(.*?)</em>',re.I|re.S|re.M)

def get_item_adv_model(page):
    html = item_adv.findall(page)[0]
    L = html.split('span>')[-1].split('<em>')
    return L

def item_price_image(shangping_id):
	return "http://price.360buyimg.com/gp%d,1.png"%int(shangping_id)

def item_shangping(url):
    return re.compile(r'<a\s*href="'+url+'">(.*?)</a>',re.I|re.M|re.S)

def str2utf(str):
    if not str:
        return ''
    else:
        return str.decode('gb18030','ignore').encode('utf8')

def extract(rule, page, single = True):
    res = rule.findall(page)
    if res:
        if single:
            return res[0]
        else:
            return res
    else:
        return None

def gen_page(url,page_id):
    return url+"&cp=%d"%page_id

def get_item_images(page):
    div = re.compile(r'(http://ec\d+.images-amazon.com/images/I/.*?_AA300_.jpg)',re.I|re.M|re.S)
    div_html = div.findall(page)
    if div_html:
        return div_html[0]
    else:
        return None

def get_shangping_fenlei(title):
    _split = title.split('-')
    return (''.join(_split[0:-2]),_split[-2])


