#!/usr/bin/env python
import gevent
from gevent.pool import Pool
from tessosx import pytesser
import Image
import urllib
from record import *


def store_path(file_name):
	from os import path
	CURRENT_PATH = path.dirname(path.abspath(__file__))
	return path.join(CURRENT_PATH, "cache",file_name)

def proxy_store(id):
	return "/Users/Seimei/Documents/Developer/cache/price/price/gp%d-1-1-3.png"%int(id)

def worker():
	while  True:
		item = q.get()
		try:
			item_id,store_id = item
			_url = "http://jprice.360buyimg.com/price/gp%d-1-1-3.png"%int(store_id)
			download_file(_url,'_','http://127.0.0.1:8091')
			_im = Image.open(proxy_store(store_id))
			_text = pytesser.image_to_string(_im)
			_res = filter(lambda ch: ch in '0123456789.', _text[2:])
			print store_id,_res
			_sql = "update item_from_360 set store_price = %f where item_id = %d"%(float(_res),int(item_id))
			DB.update(_sql)
		finally:
			q.task_done()


def custmor(job):
	item_id,store_id = job
	_url = "http://jprice.360buyimg.com/price/gp%d-1-1-3.png"%int(store_id)
	
	_f = urllib.urlopen(_url,proxies = {'http':'http://127.0.0.1:8091'})
	try:

		_im = Image.open(proxy_store(store_id))
		_text = pytesser.image_to_string(_im)
		_res = filter(lambda ch: ch in '0123456789.', _text[2:])
		print store_id,_res
		_sql = "update item_from_360 set store_price = %f where item_id = %d"%(float(_res),int(item_id))
		DB.update(_sql)
	except:
		pass
	
jobs = []
data = DB.getRows("select item_id,store_item_id from item_from_360 where store_price = 0")
for i in data:
	jobs.append([i['item_id'],i['store_item_id']])

pool = Pool(16)
pool.map(custmor,jobs)
	
