#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''
The ThreadSaft Berkeley Mode

class BaseDB(object):
    def __init__(self, hash_file, DbPath = None):
    def init(self):
    def initEvn(self):
    def verifyDB(self):
    def opendb(self):
    def create(self):
    def set(self, key, value):
    def get(self, key, defaultvalue = None):
    def __del__(self):
    def message(self, msg, log=sys.stdout):
'''

#************************
# FileName: GBaseHashMap.py
# Author: ghostwwl
# Date: 2007.11
#************************


import os
import sys
import time
from bsddb import db
#from Thread import allocate_lock
from zlib import compress, decompress

_debug = 1
_DBFLAG = db.DB_PRIVATE|db.DB_CREATE|db.DB_THREAD|db.DB_INIT_LOCK|db.DB_INIT_MPOOL

class BaseHash(object):
    '''单个bdb文件最好不要超过100万 否则性能会下降'''
    def __init__(self, hash_file, DbPath = None):
        '''hash_file bdb文件的文件名 自动回加.db
           DbPath    BDB文件保存的目录 这个目录会创建bdb环境'''
        if not DbPath:
            DbEvnPath = os.path.join(os.path.realpath(__file__), 'DAT')
        else:
            DbEvnPath = DbPath
        try:
            os.makedirs(DbEvnPath)
        except:pass
        self.RootPath = DbEvnPath
        self.hash_file = hash_file
        #Cache大小10M
        self.__CACHESIZE = 1024*1024*10
        self.pagesize = None
        self.Evn = None
        #self._Lock = Lock()
        self.initEvn()
        self._HASH = None
        self.init()
    
    def init(self):
        self.initEvn()
        if os.path.exists(os.path.join(self.RootPath, "%s.db" % self.hash_file)):
            self.opendb()
        else:
            self.create()
            
    def initEvn(self):
        '''初始化Event'''
        if self.Evn is None:
            try:                
                self.Evn = db.DBEnv()
                if  self.__CACHESIZE is not None:
                    if  self.__CACHESIZE >= 20480:
                        self.Evn.set_cachesize(0, self.__CACHESIZE, 1)
                    else:
                        raise Exception("cachesize must be >= 20480")
                #self.Evn.set_cachesize(0, self.__CACHESIZE, 1)
                dbflag = db.DB_CREATE|db.DB_INIT_MPOOL|db.DB_INIT_LOCK|db.DB_THREAD
                self.Evn.set_lk_detect(db.DB_LOCK_DEFAULT) 
                self.Evn.open(self.RootPath, _DBFLAG)
            except Exception, e:
                self.Evn = None
                raise Exception('Create DBEVENT ERROR.(%s)' % str(e))
    
    def verifyDB(self):
        '''校检db数据文件'''
        try:
            mydb = db.DB(self.Evn)
            mydb.set_get_returns_none(2)                        
            mydb.verify("%s.db" % self.hash_file, None)
            mydb.close()
            flg = True
            del mydb
        except Exception, e:
            raise Exception("VERIFY DB %s.db ERROR.(%s)" % (self.hash_file ,str(e)))
    
    def opendb(self):
        self.verifyDB()
        mdb = None
        mdb = db.DB(self.Evn)
        mdb.set_get_returns_none(2)
        if not self.pagesize:
            self.db.set_pagesize(8192)
        else:
            self.db.set_pagesize(self.pagesize)
        if mdb.open("%s.db" % self.hash_file, None, db.DB_HASH): 
            # 打开成功，返回None
            raise Exception('Open DB %s Failed' % self.hash_file)
        self._HASH = mdb
        del mdb
    
    def create(self):
        mydb = None
        mydb = db.DB(self.Evn)
        mydb.set_get_returns_none(2)        
        if mydb.open('%s.db' % self.hash_file, None, db.DB_HASH, db.DB_CREATE):
            self.message("Create DB %s Error" % self.hash_file)
        self._HASH = mydb
        del mydb
    
    def set(self, key, value):
        flg = False
        try:
            self._HASH.put(str(key), compress(str(value)))
            self.count = int(self.get('_COUNT', '0')) + 1
            if self.count % 100 == 0:
                #每100条同步一下
                self._HASH.sync()
            self._HASH.put('_COUNT', compress(str(self.count)))
            flg = True
        except Exception,e:
            self._HASH.sync()
            self.message("Set DB Error: %s" % str(e))
        finally:
            return flg
    
    def get(self, key, defaultvalue = None):
        v = self._HASH.get(str(key), None)
        if v is not None:
            return decompress(v)
        elif defaultvalue is not None:
            return defaultvalue
        else:
            return None

    def over(self):
        self._HASH.sync()
        self._HASH.close()
        self.Evn.close()
        for i in os.listdir(self.RootPath):
            #删掉磁盘上的缓存文件
            try:
                if i.startswith('__db'):
                    os.remove(os.path.join(self.RootPath, i))
            except:pass
        
    def __del__(self):
        self.over()
    
    def message(self, msg, log=sys.stdout):
        if _debug:
            print >> log, "%s] MSG %s" % (time.strftime('%Y-%m-%d %H:%M:%S'), str(msg))
    
#**************************************************************************************
from GThread import Class_Timer
import uuid
class test(object):
    def __init__(self):
        self.myhash = BaseHash("test", "r:\\TH")
        self.timer = Class_Timer()
        
    def r(self):
        u = uuid.uuid1().hex
        print self.myhash.set(u, u)
        
    def run(self):
        for i in range(10):
            self.timer.AddTimer("T%d" % i, self, 0.001, 'r')
        count = 0
        while 1:
            time.sleep(10)
            count += 1
            if count > 60:
                break


if __name__ == '__main__':
    #t = test()
    #t.run()
    a = BaseHash("test", r"r:\TH")
    f = a._HASH.keys()
#    m = open("c:\\t.txt", "wb")
#    m.write('\n'.join(f))
#    m.close()
#    
    
#    a = BaseHash("C", "r:\\DAT")
#    a.message("hello ghostwwl")
#    f = open(r'R:\sort_1.txt', 'r')
#    a.set(r'R:\sort_1.txt', f.read())
#    f.close()
#    print a.get(r'R:\sort_1.txt')


#    print a.get(1)
#    print a.get(2)
#    print a.get(3)
#    print a.get("babasdg")
#    print a.get(4)
#
#    
#    a.set(1, 'ghostwwl')
#    a.set(2, 'zhangcheng')
#    a.set(3, 'wangyou')
#    a.set(4, 'hellocat')
#    for i in range(1, 5):
#        print a.get(i)
#    for i in range(10000):
#        a.set(i**3, str(i**10))
#    a.set("name", "中国人")
#    print a.get(1000**3, 'haha')
#    print a.get("name").decode('utf-8', 'ignore').encode('gb18030', 'ignore')
#    for j in range(1000, 5000):
#        print a.get(j**3)
