#!/usr/bin/env python
#-*- coding: utf-8 -*-

#********************************************
#   FileName: memblack.py
#   Author: wule
#   Date: 2007-10-11
#   Email: ghostwwl@gmail.com
#********************************************


from cStringIO import StringIO
from threading import RLock


class MemBlack(object):
    def __init__(self, pagesize, backsize=100):
        self.memblack = StringIO()
        self.MemBlackSize = backsize
        self.Lock = RLock()
        self.PageSize = pagesize
        try:
            self.memblack.write(self.MemBlackSize*1024*1024*'\0')
            self.memblack.seek(0)
        except Exception, err:
            raise Exception(err)
        
    def isfull(self):
        flg = False
        self.Lock.acquire()
        try:
            self.memblack.seek(0, 2)
            if self.memblack.tell() >= self.MemBlackSize*1024*1024:
                flg = True
        except:
            pass
        self.Lock.release()
        return flg
        
    def write(self, pos, data):
        '''
        往memblack的pos偏移位置开始写数据
        '''
        ret = -1
        self.Lock.acquire()
        try:
            self.memblack.reset()
            self.memblack.seek(pos)
            self.memblack.write(data)
            ret = len(data)
        except:
            pass
        self.Lock.release()
        return ret
    
    def read(self, pos, bytes = -1):
        '''
        读black头的pos偏移位置读byte字节的数据
        '''
        result = None
        if bytes < 0:
            bytes = self.MemBlackSize*1024
        self.Lock.acquire()
        try:
            self.memblack.reset()
            self.memblack.seek(pos)
            result = self.memblack.read(bytes)
        except:
            pass
        self.Lock.release()
        return result
    
    def readall(self):
        '''
        读出black内所有的数据
        '''
        ret = ''
        self.Lock.acquire()
        try:
            ret = self.memblack.getvalue()
        except Exception, err:
            raise Exception(err)
        self.Lock.release()
        return ret
    
    def reuse(self, pos, bytes = -1):
        '''
        没有返回值 如果失败没关系
        写的时候就覆盖掉了
        '''
        if bytes < 0:
            bytes = self.PageSize*1024
        self.Lock.acquire()
        try:
            flg = self.write(pos, '\0'*bytes)
            if flg < 0:
                self.reuse(pos, bytes)
        except:
            pass
        self.Lock.release()
    
    def close(self):
        self.memblack.close()


if __name__ == '__main__':
    a = "测试，如果有问题就是有问题 ，如果没有问题就是没有问题，我也不知道有没有问题"
    b = "ce shi ru guo mei you wen ti jiu shi mei you wen ti ru guo you wen ti jiu shi you wen ti"
    m = MemBlack(16, 10)
    print m.write(0, b)
    r = m.read(30, 10)
    m.write(88,a)
    n = m.read(80)
    m.close()
    print n
    print r
