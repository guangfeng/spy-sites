#encoding: utf-8
import toolkit
import ConfigParser
import MySQLdb

conf = ConfigParser.ConfigParser()
conf.read('task.conf')
HOST = conf.get('mysql', 'host')
USER = conf.get('mysql', 'user')
PSWD = conf.get('mysql', 'pswd')
DB = conf.get('mysql', 'base')

DB = toolkit.MySQLClient(HOST, USER, PSWD, DB, _isdict = True)

FROM = DB.getRows("select * from item_from_suning")
for i in FROM:
	f = lambda x:MySQLdb.string_literal(x)
	#print f(i['store_adv'])
	DB.update("insert into items (`store_item_id`,`item_brand`,`item_model`,`store_title`,`item_store`, \
		`store_price`,`item_url`,`item_thumb`,`item_category`,`item_property`) values ('%s','%s','%s',\"%s\",'%s',%f,'%s','%s','%s','%s') "%(i['store_item_id'],i['item_brand'],i['item_model'],i['store_title'],'"suning"',i['store_price'],i['item_url'],i['item_thumb'],i['item_category'],i['item_property']))