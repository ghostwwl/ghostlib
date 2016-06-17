#!/usr/bin/env python
#-*- coding: utf-8 -*-

#********************************
# Name: GSqlite.py
# Author: ghostwwl
# Note:
#    Sqlite 数据库封装
#********************************

import types
import time
from threading import Lock
import sqlite3 as sqlite

class GSqlite(object):
    '''
    dbFile: Sqlite的数据文件,默认是None 创建内存表
    ENCODE: 外部写入sqlite数据的编码环境 用来创建文本工厂
            默认输入输出的数据都为utf-8
    '''
    def __init__(self, dbFile=None, ENCODE = "utf-8"):
        self.dbFile = dbFile
        self.ENCODE = ENCODE
        self.__DB = None
        self._lock = Lock()
        
    def execute(self, sql, param=None):
        '''查询输出的所有中文为unicode编码'''
        if not self.connected():
            self.connect()
            
        self._lock.acquire()
        try:
            FLAG = False
            cur = None
                
            if cur is None:
                cur = self.__DB.cursor()
                
            if cur is not None:
                if param is not None:   
                    result = cur.execute(sql, param)
                else:
                    result = cur.execute(sql)
                
                if result.description == None:
                    result = cur.rowcount
                else:
                    result = cur.fetchall()
                    
                self.__DB.commit()
                FLAG = True
                cur.close()
                cur = None
        except Exception, e:
            try:
                if self.__DB is not None:
                    self.__DB.rollback()
            except Exception, e:
                self.reconnect()
            result = 'Execute error.(%s)' % str(e)
            FLAG = False            
        self._lock.release()
        return (FLAG, result)
    
    def connected(self):
        return self.__DB is not None
    
    def reconnect(self):
        if self.__DB:
            return (True, 'Connect Sqlite %s OK.' % self.dbFile)
        else:
            return self.connect()
    
    def connect(self):
        try:
            flg = False
            result = ''
            if self.__DB is None:
                if self.dbFile is not None:
                    self.__DB = sqlite.connect(self.dbFile)
                else:
                    #如果数据文件为空 则默认创建内存数据库
                    self.__DB = sqlite.connect(":memory:")
                #文本工厂 因为sqlite是unicode保存字段，如果传进来的不是unicode
                #自动转码为unicode
#                self.__DB.text_factory = lambda x: unicode(x, self.ENCODE, "ignore")
                return (True, 'Connect Sqlite %s OK.' % self.dbFile)
        except Exception, e:
            return (False, str(e))
               
    def disconnect(self):
        if self.__DB is not None:
            self.__DB.close()
    
    def executemany(self, sqls):
        if not self.connected():
            result, ret = self.reconnect()
            if not result:
                time.sleep(0.1)
                return (result, ret)
        if self.connected():
            self._lock.acquire()
            try:
                cur = None
                cur = self.__DB.cursor()
                rlist = []
                for sql in sqls:
                    try:
                        if type(sql) in (types.ListType, types.TupleType):
                            param = sql[1]
                            sql = sql[0]
                        else:
                            param = None
                        if param == None:
                            ret = cur.execute(sql)
                        else:
                            ret = cur.execute(sql, param)
                            
                        if ret.description == None:
                              ret = cur.rowcount
                        else:
                            ret = cur.fetchall()
                            
                        result = True
                    except Exception, args:
                        ret = 'Execute error.(%s)' % str(args)
                        result = False
                    rlist.append((result, ret))
                cur.close()
                self.__DB.commit()
                result = True
                ret = rlist
            except Exception, e:
                try:
                    self.__DB.rollback()
                    if cur:
                        cur.close()
                except Exception, e:
                    self.reconnect()
                ret = 'Executemany error.(%s)' % str(e)
                result = False
            self._lock.release()
        else:
            result = False
            ret = 'Executemany error.(Connection is not found)'
        return (result, ret)

#-------------------------------------------------------------------------------    
class ClassSqlite(object):
    def __init__(self, dbname = ':memory:', encoding = ''):
        self.conn = None
        self.dbname = dbname
        self.encoding = encoding
        self.sqllock = Lock()
    
    def __del__(self):
        self.disconnect()
        
    # 连接测试
    def connect(self):
        if self.conn:
            result = True
            ret = ''
        else:
            try:
                self.conn = sqlite.connect(self.dbname)
                if self.encoding:
                    # 文本存储使用的编码，sqlite默认时使用utf-8
                    self.conn.text_factory = lambda x: unicode(x, self.encoding, 'replace')
                result = True
                ret = 'Connect sqlite "%s" OK.' % self.dbname
            except Exception, args:
                self.conn = None
                result = False
                ret = 'Connect sqlite error.(%s)' % str(args)
        return (result, ret)
    
    # 断开连接
    def disconnect(self):
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
            self.conn = None
        return 'Disconnected!'
            
    # 重新连接
    def reconnect(self, dbname = ':memory:', encoding = ''):
        self.disconnect()
        self.dbname = dbname
        self.encoding = encoding
        return self.connect()
            
    # 检查是否已连接
    def connected(self):
        return (self.conn is not None)
    
    # 执行单条语句
    # sql是一个格式化字符串，param可以是参数
    # 如：sql=insert into testdb values(?, ?)
    #     param=(1,'tom')
    # 其中param还可以是一个字典
    # 如：sql=insert into testdb values(:id, :name)
    #     param={'id':1,'name':'zc'}
    # 返回：result表示所有语句执行成功否
    #     若执行成功，ret是结果集或影响记录数(特殊：删除时不带条件，返回0)
    #     若执行失败，ret是错误提示信息
    def execute(self, sql, param=None):
        if not self.connected(): # 如果没有连接，则先尝试连接
            self.sqllock.acquire()
            result, ret = self.reconnect(self.dbname, self.encoding)
            self.sqllock.release()
            if not result:
                time.sleep(0.1) # 防止重复执行时，把CPU占满
                return (result, ret)
        if self.connected():
            self.sqllock.acquire()
            try:
                cur = None
                cur = self.conn.cursor()
                if param != None:
                    # 转换单变量参数为列表参数
                    if type(param) not in (list, tuple, dict):
                        param = [param]
                    ret = cur.execute(sql, param)
                else:
                    ret = cur.execute(sql)
                if ret.description == None: # 如果有执行结果，返回影响的个数，否则返回None
                    ret = cur.rowcount
                else:
                    ret = cur.fetchall()
                result = True
                cur.close()
                self.conn.commit()
            except Exception, args:
                try:
                    self.conn.rollback()
                    if cur:
                        cur.close()
                except Exception:
                    self.reconnect(self.dbname, self.encoding)
                ret = 'Execute error.(%s)' % str(args)
                result = False
            self.sqllock.release()
        else:
            result = False
            ret = 'Execute error.(Connection is not found)'
        return (result, ret)
    
    # 执行多条语句
    # sqllist是一个语句列表，其每个元素可以是一个sql字符串，也可以是(sql,param)
    # 返回：result表示所有语句执行过程是否成功
    #     若过程成功，ret是每条语句的执行结果（同执行单条语句的返回）
    #     若过程失败，ret是错误提示信息
    def executemany(self, sqllist, checklob=False):
        if not self.connected(): # 如果没有连接，则先尝试连接
            self.sqllock.acquire()
            result, ret = self.reconnect(self.dbname, self.encoding)
            self.sqllock.release()
            if not result:
                time.sleep(0.1) # 防止重复执行时，把CPU占满
                return (result, ret)
        if self.connected():
            self.sqllock.acquire()
            try:
                cur = None
                cur = self.conn.cursor()
                rlist = []
                for sql in sqllist:
                    try:
                        if type(sql) in (list, tuple):
                            param = sql[1]
                            sql = sql[0]
                        else:
                            param = None
                        if param == None:
                            ret = cur.execute(sql)
                        else:
                            # 转换单变量参数为列表参数
                            if type(param) not in (list, tuple, dict):
                                param = [param]
                            ret = cur.execute(sql, param)
                        if ret.description == None:
                            ret = cur.rowcount
                        else:
                            ret = cur.fetchall()
                        result = True
                    except Exception, args:
                        ret = 'Execute error.(%s)' % str(args)
                        result = False
                    rlist.append((result, ret))
                cur.close()
                self.conn.commit()
                result = True
                ret = rlist
            except Exception, args:
                try:
                    self.conn.rollback()
                    if cur:
                        cur.close()
                except Exception:
                    self.reconnect(self.dbname, self.encoding)
                ret = 'Executemany error.(%s)' % str(args)
                result = False
            self.sqllock.release()
        else:
            result = False
            ret = 'Executemany error.(Connection is not found)'
        return (result, ret)

#-------------------------------------------------------------------------------        
def test():
    T = GSqlite()
    print T.connect()
    flg, ret = T.execute("select name from sqlite_master where name='test'")
    print T.execute("select * from sqlite_master")
    if len(ret) == 0:
        print T.execute('''Create Table test(
            id integer primary key,
            user text not null)''')
    for j in range(100):
        print T.execute("insert into test(user) values('好人')")
    print T.execute("select *  from test")
    s = []
    for i in range(65, 91):
        s.append(("insert into test(user) values(?)", (chr(i),)))
    print T.executemany(s)
    print "**********"
#    print T.execute("update test set user = 'mm'")
    print T.execute("select * from test where id > 10")
    print T.execute("select *  from test")
    print T.execute("insert into test(user) values(?)", (u'aa',))
    T.disconnect()
    
    
    

if __name__ == '__main__':
    test()
#    T = GSqlite("sp.db")
#    print T.execute("update sp set outurl = ? where link = ?", (1, "http://www.baidu.com"))
