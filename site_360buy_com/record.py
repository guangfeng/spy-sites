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

def data_record(data):
    """
    """
    store_item_id = int(data['item_id'])
    item_brand = data['brand']
    item_model = data['model']
    store_title = MySQLdb.string_literal(data['title'])
    store_desc = MySQLdb.string_literal(data['desc'])
    store_adv = MySQLdb.string_literal(data['adv'])
    store_price = float(data['current_price'])
    item_url = data['item_url']
    item_thumb = MySQLdb.string_literal(data['item_thumb'])
    item_category = MySQLdb.string_literal(data['category'])
    item_property = MySQLdb.string_literal(data['property'])

    rec_sql_template = "insert into item_from_360 (`store_item_id`,`item_brand`,`item_model`,`store_title`,`store_desc`, \
    `store_adv`, `store_price`, `item_url`, `item_thumb`, `item_category`, `item_property`, `_created`, `_updated`) values (%d, '%s', '%s', %s, %s, %s, \
    %f, '%s', %s, %s, %s, now(), now())"%(store_item_id, item_brand, item_model, store_title, store_desc,store_adv,store_price,item_url,item_thumb,item_category,item_property)

    return DB.update(rec_sql_template)

def add_task_price(item_id, image_link):
    """
    """
    item_id = int(item_id)
    image = MySQLdb.string_literal(image_link)

    price_task_template = "insert into price_360_task (`image`, `item_id`) values (%s, %d)"%(image, item_id)
    return DB.update(price_task_template)
    
    

if __name__ == "__main__":
    print data_record({'item_id':100000,'brand':'MUJI','model':'无影教','title':'有关无影脚的测试','desc':'这是一个飞速的无影脚，超级牛逼的说','adv':'无影脚现在只要998，注意是998哦! 不是1998','current_price':998.1,'item_url':'www.google.com','item_thumb':'www'})

    print add_task_price(1001, 'http://www.baidu.com')
    
    
