#!/usr/bin/env python
#encoding:utf8
'''
base tools about
http-downloader,
charset convert,
mysql connection,
'''
import os
import re
import socket
import urllib2
import cookielib
import bsddb3 as bsddb
import MySQLdb
import MySQLdb.cursors
import time
import chardet
import Levenshtein

#=== local module =========
import baseconst
import platform
if platform.system() == "Darwin":
    from ctypes import *
    fnvhash = CDLL('fnvhash.dylib')
else:
    import fnvhash

class MySQLClient:
    '''connection to MySQL database, with simple interface:
    check:        return True or Fasle the input sql
    getRow:     return one row of the input sql
    getRows:    return all rows of the input sql
    update:     update the database with the input sql, which include UPDATE, INSERT, DELETE
    '''
    def __init__(self, _db_host, _db_user, _db_passwd, _db_db,
                  _isdict = None, max_idle_time=7*3600):
        self.__host = _db_host
        self.__user = _db_user
        self.__passwd = _db_passwd
        self.__db = _db_db
        self.__conn = None
        self.__last_use_time = time.time()
        self.max_idle_time = max_idle_time
        self.__isdict = _isdict

    def __del__(self):
        self.close()

    def close(self):
        """Closes this database connection."""
        if getattr(self, "__conn", None) is not None:
            self.__conn.close()
            self.__conn = None

    def reconnect(self):
        """Closes the existing database connection and re-opens it."""
        self.close()
        if self.__isdict:
            self.__conn = MySQLdb.connect(
               host=self.__host,
               user=self.__user,
               passwd=self.__passwd,
               db=self.__db,
               charset='utf8',
               cursorclass=MySQLdb.cursors.DictCursor)
        else:
            self.__conn = MySQLdb.connect(
               host=self.__host,
               user=self.__user,
               passwd=self.__passwd,
               db=self.__db,
               charset='utf8',
               )
        #self.__conn.autocommit(True)

    def _ensure_connected(self):
        # Mysql by default closes client connections that are idle for
        # 8 hours, but the client library does not report this fact until
        # you try to perform a query and it fails. Protect against this
        # case by preemptively closing and reopening the connection
        # if it has been idle for too long (7 hours by default).
        if (self.__conn is None or
            (time.time() - self._last_use_time > self.max_idle_time)):
            self.reconnect()
        self._last_use_time = time.time()

    def _cursor(self):
        self._ensure_connected()
        return self.__conn.cursor()

    def check(self, sql):
        '''
        check something in db or not
        '''
        cur = self._cursor()
        try:
            c = cur.execute(sql)
            if c > 0:
                cur.close()
                return True
            #cur.close()
            return False
        finally:
            cur.close()
            pass

    def getRow(self, sql):
        '''
        input: your select sql, e.g. "SELECT * FROM table_name WHERE id > 10"
        return: one row
        '''
        data = []
        try:
            cur = self._cursor()
            c = cur.execute(sql)
            if c>0:
                data = cur.fetchone()
                cur.close()
                return data
        except Exception, e:
            print baseconst.RED, "mysql error: ", e, baseconst.NOR
            print baseconst.BLU, "the sql is : ", sql, baseconst.NOR
            
            return data
        finally:
            cur.close()
            pass

    def getRows(self, sql):
        '''
        input: your select sql, e.g. "SELECT * FROM table_name WHERE id > 10"
        return: the data
        '''
        data = []
        try:
            cur = self._cursor()
            c = cur.execute(sql)
            if c>0:
                data = cur.fetchall()
                cur.close()
                return data
            else:
                cur.close()
                return ()
        except Exception, e:
            print baseconst.RED, "mysql error: ", e, baseconst.NOR
            print baseconst.BLU, "the sql is : ", sql, baseconst.NOR
            return data
        finally:
            cur.close()

    def update(self, sql):
        '''
        change DB with data in "sql"
        '''
        try:
            cur = self._cursor()
            c = cur.execute(sql)
            self.__conn.commit()
            cur.close()
            return c
        except Exception, e:
            print baseconst.RED, "mysql error: ", e, baseconst.NOR
            print baseconst.BLU, "the sql is : ", sql, baseconst.NOR
            
        finally:
            cur.close()
            

class Index:
    '''index of string to chech string is processed or not,
         it is useful for crawler to record url processed.
         it use bsddb(b+tree) to record & check the string'''
    def __init__(self, _idx_file):
        self.__db = bsddb.btopen(_idx_file, 'c')
        
    def __del__(self):
        self.__db.close()
        
    def has(self, _key):
        '''return True if has label,
        otherwise, insert into index and then return False'''

        if self.__db.has_key(_key):
            return True
        return False
    def get(self, _key):
        return self.__db.get(_key)

    def insert(self, _key, _value='a'):
        #insert to __db if not had
        self.__db[_key] = _value #time.strftime('%Y-%m-%d %H-%M-%S')
        self.__db.sync()
        return True
    

'''useful functions'''
def getDomain(host):
    '''domain here is usually a second-level domain, which belongs to a Company/Unit (e.g. Google/Youtube)
    the implementation is to remove sub-domain in the host
    '''
    d = ''
    t = host.split('.')
    c = len(t)
    pos = c-1
    while pos > -1:
        if t[pos] in baseconst.ToplevelDomain:
            if pos == c-1:
                d = t[pos]
            else:
                d = t[pos] + '.' + d
            pos -=1
            continue
        d = t[pos] + '.'    + d
        break
    return d

def getHost(url):
    b = e = slash = 0
    pos = -1
    for c in url:
        pos += 1
        if c == ':':
            if b == 0:
                continue
            else:
                e = pos
                break
        elif c == '/':
            if slash == 2:
                e = pos
                break
            slash += 1
        elif slash == 2 and c.isalnum():
            if b == 0:
                b = pos
    host = ''
    if b < e:
        host = url[b:e]
    return host

def zh2utf8(istr):
    '''Auto convert encodings to utf8'''
    istr = istr.strip()
    #print istr[:1000]
    charset = chardet.detect(istr[:1000])['encoding']
    print charset
    if charset is None:
        print baseconst.BRO, 'can not detect encoding of content: ', istr, baseconst.NOR
        return istr
    charset = charset.upper()
    if (charset != 'UTF-8') and (charset != 'ISO-8859-2'):
        ## utf8 Chinese with lots of English charactor in HTML TAGs will
        ## be guessed as ISO-8859-2 by chardet
        print 'other: ', charset
        if charset == 'GB2312':
            charset = 'GB18030'
        try:
            istr = istr.decode(charset).encode('utf8')
        except Exception, e:
            print e
            return istr
    elif charset == 'ISO-8859-2':
        try:
           istr = istr.decode('utf-8').encode('utf8')
        except:
           istr = istr.decode('gb18030').encode('utf8')
    return istr

def downloader(url, cookie=False, timeout=30):
    
    socket.setdefaulttimeout(timeout)
    if cookie:
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)
    req = urllib2.Request(url)
    req.add_header(
        'User-Agent',
        "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv: 1.9.0.15) \
            Gecko/2009102814 Iceweasel/3.0.6 (Debian-3.0.6-3)")
    #req.add_header('Host',getHost(url))
    try:
        fd   = urllib2.urlopen(req)
        data = fd.read()
        return data
    except Exception, e:
        print baseconst.BRO, e, baseconst.NOR
        print baseconst.RED, 'can not download: ', url, baseconst.NOR
        return 'nothing'

def normalizeUrl(urlToParsed, urlReffer):
    '''normalize the urlToParsed from html with it's reffer'''
    urlToParsed = urlToParsed.replace('&amp;', '&')
    if urlToParsed.startswith('http://'):
        return urlToParsed
    if urlToParsed.startswith('/'):
        host = getHost(urlReffer)
        goodUrl = 'http://' + host + urlToParsed
        return goodUrl
    if urlToParsed.startswith('mailto:'):
        return ''
    if urlToParsed.startswith('javascript:'):
        return ''
    ## urlToParsed likes 'abc.html', whiech needs urlReffer's dir path
    while urlToParsed.startswith('.'):
        if urlToParsed.startswith('./'):
            urlToParsed = urlToParsed[2:]
        elif urlToParsed.startswith('../'):
            urlToParsed = urlToParsed[3:]
        else: #not support
            break
    if '?' in urlReffer[0]:
        pos = urlReffer.rfind('?')
        goodUrl = urlReffer[:pos] + urlToParsed
    else:
        pos = urlReffer.rfind('/')
        goodUrl = urlReffer[:pos] + '/' + urlToParsed
    return goodUrl

p_script = re.compile(r'<script(?:\n|.)*?</script>', re.I|re.M|re.S)
p_style  = re.compile(r'<style(?:\n|.)*?</style>', re.I|re.M|re.S)
p_rmTags = re.compile(r"<[^>](?:[^>]|\n)*>", re.M|re.S)
p_nbsp = re.compile(r'&nbsp[;]?', re.I)
def getTextFromHtml(html):
    text = p_script.sub('', html)
    text = p_style.sub('', text)
    text = p_rmTags.sub('', text)
    text = p_nbsp.sub('', text)
    return text

def removeHtmlTag(istr):
    ''' remove html tag included in 'istr' '''
    patten_rmTag = r"<[^>](?:[^>]|\n)*>" #remove <tag>
    return re.sub(patten_rmTag, '', istr)

def uniqify(seq):
    '''Fastest way to uniqify a list in Python
    ref: http://www.peterbe.com/plog/uniqifiers-benchmark/'''
    # Not order preserving
    return list(set(seq))

def genPageshot(url, topdir, mkdatedir=True ):
    path = topdir
    if mkdatedir:
        path = topdir + '/' + time.strftime('%Y/%m/%d/')
        if not os.path.isdir(path):
            os.makedirs(path)
    host = getHost(url)
    now4file = time.strftime('%Y-%m-%d-%H-%M-%S')
    shotfile = host + '_' + now4file + '.jpg'
    shotpath = path + '/' + shotfile
    shotpath = shotpath.replace('//', '/')
    cmd = 'xvfb-run -a --server-args="-screen 0, 1024x768x24" \
            ./CutyCapt --user-agent=Mozilla --javascript=off --max-wait=180000 \
            --url="' + url + '" --out=' + shotpath
    rt = os.system(cmd)
    print rt
    good = True
    if not os.path.exists(shotpath):
        good = False
    return (good, shotpath)

def print_list(ls):
    for l in ls:
        print l

def print_dict(dc):
    for k in dc:
        print k,': ', dc[k]

def initLogger(logfile, file_max_size=2*1024*1024):
    '''usage:
    mylogger = initLogger('mylog.log')
    mylogger.debug('debugging message')
    mylogger.error('error message')
    mylogger.info('info message')
    '''
    import logging
    import logging.handlers
    logger = logging.getLogger()
    #hdlr = logging.FileHandler(logfile)
    hdlr = logging.handlers.RotatingFileHandler(
            filename=logfile,
            maxBytes=file_max_size,
            backupCount=3)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    return logger

def defrag_txt(txt):#for unicode
    result = []
    pre_is_en = False
    stop_word = set(u' ,.。?!')
    for i in txt:
        num_i = ord(i)
        if i not in stop_word:
            if 0x4e00 <= num_i < 0x9fa6:
                result.append(i)
                continue
            if 97 <= num_i <= 122 or 65 <= num_i <= 90:
                result.append(i)
                pre_is_en = True
                continue
            if 48 <= num_i <= 57:
                result.append(i)
                continue
            num_diff = num_i-0xff10
            if 0 <= num_diff < 10:
                result.append(str(num_diff))
                continue
            pre_is_en = False
        else:
            if pre_is_en:
                result.append(i)
                pre_is_en = False
    return ''.join(result)

def get_32_hash(input_data):
    if isinstance(input_data, unicode):
        input_data = input_data.encode('utf-8')
    output = fnvhash.fnv_32a_str(input_data)
    return output

def get_64_hash(input_data):
    if isinstance(input_data, unicode):
        input_data = input_data.encode('utf-8')
    output = fnvhash.fnv_64a_str(input_data)
    return output


class Levenshtein_score():
    def __init__(self,):
        #self.root_datas = []
        #先取5000条，如果无则不取
        self.root_pool = []
    def _root_pool(self, l_datas):
        for t in l_datas:
            self.root_pool.append((t['id'], t['title']))
        
            
    def lev_score(self, t1, t2):
    
        if isinstance(t1, unicode):
            t1 = defrag_txt(t1)
        if isinstance(t2, unicode):
            t2 = defrag_txt(t2)
        elif isinstance(t2, str):
            t2 = defrag_txt(t2.decode('utf-8'))
        #print [t1,t2]
        if not (t1 and t2):
            return False
        score = Levenshtein.ratio(t1, t2)
        if score >= 0.8:
            return True
        return False
    def put(self, l_id, l_title):
        self.root_pool.pop(0)
        self.root_pool.append((l_id, l_title))
    def run(self, t_1):
        #if not root_pool:
        #   root_pool.append(t1)
        if isinstance(t_1, str):
            t_1 = t_1.decode('utf-8')
        for t_2 in self.root_pool:
            t_s = self.lev_score(t_1, t_2[1])
            if t_s:
               return t_2[0]
        return
               

## test
if __name__ == '__main__':
    url = [
            'http://jining.sdnews.com.cn/News/760/206928.html',
            'http://www.google.com.hk/search?q=%E6%9D%8E%E5%88%9A&hl=zh-CN&safe=strict&tbs=frm:1&source=lnms',
            ]
    ## test normalizeUrl()
    urls = {
            './../abc.html': 'http://example.com/dir1/1.html',
            '../../abc.html': 'http://example.com/dir1/1.html',
            '/abc.html':'http://example.com/dir1/1.html',
            'abc.html': 'http://example.com/dir1/1.html',
            }
    for k,v in urls.items():
        nz = normalizeUrl(k, v)
        print '%s ==> %s' % (k, nz)

    #testing MySQLClient
    db = MySQLClient('localhost', 'root', 'toor', 'weipingjia')
    sql = 'select * from process_class_words limit 10'
    data = db.getRows(sql)
    print 'count: ', len(data)
    for d in data:
        for i in d:
            print '\t', i
        print '.......\n'
    sql = 'insert into z_cluster set pid=1, serial_no=1, is_new=1, phrase="abc"'
    for i in range(10):
        db.update(sql)
