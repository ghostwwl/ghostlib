#!/usr/bin/env python
#-*- coding:utf-8

#********************************
#   FileName: pxaliyun.py
#   Author  : ghostwwl
#   Note    : 本地整目录图片上传待aliyun oss
#             Wx gui库依赖
#*******************************

import re
import os
import time
import Queue
from GThread import Class_Timer

import wx
import wx.richtext
import wx.lib.buttons


import stat
import datetime
from glob import glob
from timeit import default_timer
#import Image
from oss.oss_api import *
from oss.oss_util import *
from oss.oss_xml_handler import *


def has_oss_obj(ossobj, dobject):
    res = ossobj.head_object('imgs-c2c-artxun-com', dobject)
    if 200 == res.status:
        return True
    return False

def check_file_size(local_file_path):
    return 
    stat_info = os.stat(local_file_path)
    file_size = stat_info[stat.ST_SIZE]/1048576.0
    #file_create_day = '%d-%d-%d' % time.gmtime(stat_info[stat.ST_CTIME])[:3]
    if file_size >= 1.3:
	try:
	    #im = Image.open(local_file_path)
	    #im.save(local_file_path, quality=80)
	    del im
	except Exception, e:pass
	
    
    
def timehead():
    return "%s] " % time.strftime("%Y/%m/%d %H:%M:%S")


def upload_dir(pobj, file_path):
    
    pobj.append_log('%s 开始检索输入目录图片文件' % timehead())
    
    wait_do_files = glob(os.path.join(file_path, '*.jpg'))
    wait_do_files.extend(glob(os.path.join(file_path, '*.JPG')))
    wait_do_files.extend(glob(os.path.join(file_path, '*.jpeg')))
    wait_do_files.extend(glob(os.path.join(file_path, '*.JPEG')))
    wait_do_files.extend(glob(os.path.join(file_path, '*.png')))
    wait_do_files.extend(glob(os.path.join(file_path, '*.PNG')))
    wait_do_files.extend(glob(os.path.join(file_path, '*.bmp')))
    wait_do_files.extend(glob(os.path.join(file_path, '*.BMP')))
    
    hash_files = {}.fromkeys(wait_do_files)
    wait_do_files = hash_files.keys()
    
    if len(wait_do_files) < 1:
	pobj.append_log('%s 此目录没有图片文件' % timehead());
	return
    
    pobj.append_log('%s 你选择的目录找到 %d 张图片需要上传...' % (timehead(), len(wait_do_files)))
    pobj.append_log('%s 开始初始化阿里云上传插件....' % timehead())
    _start_time = default_timer()
    ossobj = OssAPI('××××××××××××××××××', '××××××××××××××××××', '××××××××××××××××××')
    ossobj.show_bar = False
    ossobj.set_send_buf_size(8192)
    ossobj.set_recv_buf_size(10485760)
    ossobj.set_debug(False)
    
    content_type = ""
    headers = {}
    
    total_up = 0
    total_all = 0
    total_failed = 0
    total_aup = 0
    
    pobj.append_log('%s 初始化输出日志...' % timehead())
    out_log_txt = os.path.join(file_path, '%s.txt' % datetime.datetime.now().strftime('%Y%m%d'))
    pobj.tcsavePath.SetValue(out_log_txt)
    out_log = open(out_log_txt, 'w')
    pobj.append_log('%s 初始化完成, 准备上传...' % timehead())
    for local_file_path in wait_do_files:
	try:
	    total_all += 1
	    tmp_obj = 'ypwj/%s/%s' % (datetime.datetime.now().strftime('%Y%m%d'), os.path.basename(local_file_path).lower())
	    
	    try:
		    out_log.write('http://××××××/%s\n' % tmp_obj)
		    out_log.flush()
	    except:pass
	    
	    if not has_oss_obj(ossobj, tmp_obj):
		check_file_size(local_file_path)
		res = ossobj.put_object_from_file('imgs-c2c-artxun-com', tmp_obj, local_file_path, content_type, headers)
		if res.status == 200:
		    total_up += 1
		    pobj.append_log('%s upload file %s [ OK ]' % (timehead(), tmp_obj));
		else:
		    total_failed += 1
		    pobj.append_log('%s upload file %s [ failed ]' % (timehead(), tmp_obj));
	    else:
		total_aup += 1
		pobj.append_log('%s file %s aleardy upload [ ok ]' % (timehead(), tmp_obj));
	except Exception, e:
	    pobj.append_log('%s uploade file %s [ error ]. err(%s)' % (timehead(), tmp_obj, str(e)));
    out_log.close()
     
    _do_task_time = default_timer()
    pobj.append_log('-------------------------------------------------------------')
    pobj.append_log('%s       all file:  %d' % (timehead(), total_all))
    pobj.append_log('%s      upload ok:  %d' % (timehead(), total_up))
    pobj.append_log('%s  upload failed:  %d' % (timehead(), total_failed))
    pobj.append_log('%s    skip upload:  %d' % (timehead(), total_aup))
    pobj.append_log('%s    do task use:  %s' % (timehead(), str(_do_task_time - _start_time)))
    
            

#****************************************************************************************
[wxID_DIALOG1, wxID_DIALOG1BTNPARSE, wxID_DIALOG1DOWNLOADCOUNT, 
 wxID_DIALOG1INURL, wxID_DIALOG1RICHTEXTCTRL1, wxID_DIALOG1SAVEPATH, 
 wxID_DIALOG1STATICBOX1, wxID_DIALOG1STATICTEXT1, wxID_DIALOG1STATICTEXT2, 
 wxID_DIALOG1STATICTEXT3, 
] = [wx.NewId() for _init_ctrls in range(10)]

class mainFrame(wx.Frame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_DIALOG1, name='', parent=prnt,
                           pos=wx.Point(361, 207), size=wx.Size(797, 532),
                           style=wx.DEFAULT_FRAME_STYLE, title=u'××××××图片上传')
        self.SetClientSize(wx.Size(789, 502))
        #self.SetIcon()

        self.staticText1 = wx.StaticText(id=wxID_DIALOG1STATICTEXT1,
                                         label=u'待上传图片目录：',
                                         name='staticText1', parent=self, pos=wx.Point(8, 16),
                                         size=wx.Size(136, 16), style=0)
        self.staticText1.SetToolTipString('')
        self.staticText1.SetHelpText('')
        #self.staticText1.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL,
                                         #False, 'SimSun'))

        self.tcinUrl = wx.TextCtrl(id=wxID_DIALOG1INURL, name='inUrl',
                                   parent=self, pos=wx.Point(160, 16), size=wx.Size(480, 22),
                                   style=0, value='')

        self.btnParse = wx.lib.buttons.GenButton(id=wxID_DIALOG1BTNPARSE,
                                                 label=u'开始上传', name='btnParse',
                                                 parent=self, pos=wx.Point(672, 16), size=wx.Size(79, 58),
                                                 style=0)
        self.btnParse.Bind(wx.EVT_BUTTON, self.OnBtnParseButton,id=wxID_DIALOG1BTNPARSE)

        self.staticBox1 = wx.StaticBox(id=wxID_DIALOG1STATICBOX1,
                                       label=u'上传进度', name='staticBox1',
                                       parent=self, pos=wx.Point(16, 80), size=wx.Size(744, 344),
                                       style=0)
        
        self.logOut = wx.TextCtrl(id=wxID_DIALOG1RICHTEXTCTRL1,
	                            parent=self, pos=wx.Point(32, 104), size=wx.Size(704, 304),
	                            style=wx.richtext.RE_MULTILINE, value='')
        
        self.staticText2 = wx.StaticText(id=wxID_DIALOG1STATICTEXT2, label='',
                                         name='staticText2', parent=self, pos=wx.Point(16, 40),
                                         size=wx.Size(0, 14), style=0)

        self.staticText3 = wx.StaticText(id=wxID_DIALOG1STATICTEXT3,
                                         label=u'日志 保 存 地址：',
                                         name='staticText3', parent=self, pos=wx.Point(8, 48),
                                         size=wx.Size(144, 16), style=0)

        self.tcsavePath = wx.TextCtrl(id=wxID_DIALOG1SAVEPATH, name='savePath',
                                      parent=self, pos=wx.Point(160, 48), size=wx.Size(480, 22),
                                      style=0, value='')

        self.downloadCount = wx.StaticText(id=wxID_DIALOG1DOWNLOADCOUNT,
                                           label=u'',
                                           name='downloadCount', parent=self, pos=wx.Point(24, 432),
                                           size=wx.Size(64, 14), style=0)

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.flv_save_path = None
	self.timer = Class_Timer()
        self.log = Queue.Queue()
        self.over_flag = False
        self.timer.AddTimer('updatelog', self, 0.1, 'update_log')
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        
    def OnClose(self, event): 
        self.timer.Stop()
        wx.Exit()
    
    def on_restar(self):
        self.tcinUrl.SetValue(u'')
        self.logOut.SetValue(u'')
        
    def OnBtnParseButton(self, event):
        txt_inurl = self.tcinUrl.GetValue()
        if not txt_inurl:
            self.append_log('%s 请输入图片目录' % timehead())
            event.Skip()
	
	    
	upload_dir(self, txt_inurl)
	  
        
    def on_update_log(self, event):
        self.update_log()
        
    def update_log(self):
        #输入日志到日志textCtrl
        log = None
        try:
            log = self.log.get_nowait()
        except:pass
        
        if log:
            logs = self.logOut.GetValue()
            logs = log.decode('utf-8', 'ignore') + logs
            self.logOut.SetValue(logs)
    
    def append_log(self, log):
        log = '%s\n' % log
        self.log.put(log)        
        
        

#****************************************************************************************
class myapp(wx.App):
    def OnInit(self):
        self.main = mainFrame(None)
        self.main.Show()
        self.SetTopWindow(self.main)
        return True

def main():
    application = myapp(0)
    application.MainLoop()
#****************************************************************************************
        
if __name__ == '__main__':
    main()
 
    
    
	
	
