#!/usr/bin/env python
#coding=utf-8

#********************************
# FileName: Spider.py
# Author: ghostwwl
# Note: 基于有限状态机模式
#       爬虫测试呢 清理硬盘找出来的 因该是08-09年的吧 
#********************************

import time
import random

class Spider(object):
    #爬虫工作的基础类
    def __init__(self, name):
        self.SpiderName = name
    
    def InitSpider(self):
        print "Spider %s GetTask..." % self.SpiderName
        pass
    
    def DownLoadFactory(self):
        print "Spider %s Downlaoding..." % self.SpiderName
        pass
 
    def ParseFactory(self):
        print "Spider %s Parsing..." % self.SpiderName
        pass
    
    def WriteBackFactory(self):
        print "Spider %s Writing..." % self.SpiderName
        pass
    
    def TaskFinish(self):
        print "Spider %s Finish..." % self.SpiderName
        pass
        
    def attach_fsm(self, state, fsm):
        #加入状态机
        self.Fsm = fsm
        self.curr_state = state
        
    def change_state(self, new_state, new_fsm):
        #状态转换
        self.curr_state = new_state
        self.Fsm.exit_state(self) #退出老的状态
        self.Fsm = new_fsm #生成新的状态
        self.Fsm.enter_state(self) #进入新的状态
        self.Fsm.exec_state(self) #执行新的状态
    
    def keep_state(self):
        #状态保持
        self.Fsm.exec_state(self)

#-------------------------------------------------------------------------------    
class BaseFsm(object):
    #状态机虚类
    def enter_state(self, obj):
        #进入状态入口
        raise NotImplementedError()
 
    def exec_state(self, obj):
        #执行对应状态工作
        raise NotImplementedError()
 
    def exit_state(self, obj):
        #退出状态
        raise NotImplementedError()

#-------------------------------------------------------------------------------
class InitSpider_Fsm(BaseFsm):
    #爬虫初始化状态
    def enter_state(self, obj):
        print "Spider %s enter Init State!" % obj.SpiderName
        
    def exec_state(self, obj):
        print "Spider %s in Init State!" % obj.SpiderName
        
    def exit_state(self, obj):
        print "Spider %s exit Init State!" % obj.SpiderName

#-------------------------------------------------------------------------------
class DownLoadFactory_Fsm(BaseFsm):
    #处理下载工作状态
    def enter_state(self, obj):
        print "Spider %s enter Download state!" % obj.SpiderName
 
    def exec_state(self, obj):
        print "Spider %s in Download state!" % obj.SpiderName
        obj.DownLoadFactory()
 
    def exit_state(self, obj):
        print "Spider %s exit Download state!" % obj.SpiderName

#-------------------------------------------------------------------------------        
class ParseFactory_Fsm(BaseFsm):
    #处理解析工作状态
    def enter_state(self, obj):
        print "Spider %s enter Parse state!" % obj.SpiderName
 
    def exec_state(self, obj):
        print "Spider %s in Parse state!" % obj.SpiderName
        obj.ParseFactory()
 
    def exit_state(self, obj):
        print "Spider %s exit Parse state!" % obj.SpiderName
        
#-------------------------------------------------------------------------------
class WriteBack_Fsm(BaseFsm):
    #处理回写工作状态
    def enter_state(self, obj):
        print "Spider %s enter Download state!" % obj.SpiderName
    
    def exec_state(self, obj):
        print "Spider %s in Download state!" % obj.SpiderName
        obj.WriteBackFactory()
    
    def exit_state(self, obj):
        print "Spider %s exit Download state!" % obj.SpiderName
        
#-------------------------------------------------------------------------------
class TaskFinish_Fsm(BaseFsm):
    #处理回写工作状态
    def enter_state(self, obj):
        print "Spider %s enter TaskFinish state!" % obj.SpiderName
    
    def exec_state(self, obj):
        print "Spider %s in TaskFinish state!" % obj.SpiderName
        obj.TaskFinish()
    
    def exit_state(self, obj):
        print "Spider %s exit TaskFinish state!" % obj.SpiderName
        
#-------------------------------------------------------------------------------
class FsmControl(object):
    #状态机管理器
    def __init__(self):
        #主要是初始化所有状态实例
        self._fsms = {}
        self._fsms[0] = InitSpider_Fsm()
        self._fsms[1] = DownLoadFactory_Fsm()
        self._fsms[2] = ParseFactory_Fsm()
        self._fsms[3] = WriteBack_Fsm()
        self._fsms[4] = TaskFinish_Fsm()
       
    def get_fsm(self, state):
        return self._fsms[state]
    
    def add_fsm(self, fsm_index, FSM):
        self._fsms[fsm_index] = FSM()
       
    def Frame(self, objs, state):
        for obj in objs:
            if state == obj.curr_state:
                obj.keep_state()
            else:
                obj.change_state(state, self._fsms[state])

#-------------------------------------------------------------------------------
class runEvent(object):
    #模拟运行环境
    def init(self):
        self._spiders = []
        self._FsmControl = FsmControl()
        self.initSpiders()
 
    def initSpiders(self):
        for i in xrange(100):#生成爬虫
            spider = Spider("SPIDER_%d" % (i+1,))
            spider.attach_fsm(0, self._FsmControl.get_fsm(0))
            self._spiders.append(spider)
 
    def __Frame(self):
        #执行状态帧
        self._FsmControl.Frame(self._spiders, StateFactory())
 
    def run(self):
        while True:
            self.__Frame()
            time.sleep(0.5)
            
#-------------------------------------------------------------------------------
def StateFactory():
    #模拟驱动爬虫状态
    return random.choice((0, 1, 2, 3, 4))
    
if __name__ == "__main__":
    T = runEvent()
    T.init()
    T.run()

    
