#!/usr/bin/env python
#-*- coding:utf-8 -*-

#--------------------------------
#Date: 2009-02-23
#Author: ghostwwl
#Revision: 1.0
#--------------------------------
#Copyright (C) video.artxun.com(ghostwwl@gmail.com)

'''
converted video files to flv format filetype
only support ('.mpeg', '.mpg', '.avi', '.asf', '.mp4', '.asx','.wmv', '.3gp', 
'.mov', '.swf',  '.dat')
auto split larger video files to multiple files of flv format
'''

import os
import re
import sys
import time
import threading
from datetime import datetime
#import win32ui, win32con

#_CODE_RATE=500
_CODE_EXISTS = ('.mpeg', '.mpg', '.avi', '.asf', '.mp4', '.asx',
                '.wmv', '.3gp', '.mov', '.swf')
time_reg = re.compile( "(\d+):(\d{2}):(\d{2}\.?\d*)" )

#def GetFiles():
#    openflag = "JPEG File (*.jpg)|*.jpg|ALL File (*.*)|*.*|"
#    filedialog = win32ui.CreateFileDialog(1, None, None, win32con.OFN_ALLOWMULTISELECT|win32con.OFN_HIDEREADONLY, openflag)
#    filedialog.SetOFNTitle("Select files to Work")
#    filedialog.DoModal()
#    
#    return filedialog.GetPathNames()

class Ticker(object):
    def __init__(self):
        self.tick = True
        self.count = 0

    def run(self):
        while self.tick:
            print ".",
            self.count += 1
            if self.count == 10:
                print "\b"*20,
                self.count = 0
            time.sleep(0.10)

class Conver_Flv(object):
    def __init__(self, srcPath, dstPath, code_byte='320', split_time=60, user_initial_mass=False):
        self.src_path = srcPath
        self.dst_path = dstPath
        self._CODE_RATE = code_byte
        self.SPLIT_TIME = split_time #这里是分钟 数值范围为[1-59]
        if self.SPLIT_TIME > 60:
            self.SPLIT_TIME = 60
        if self.SPLIT_TIME < 5:
            self.SPLIT_TIME = 5
        self.user_initial_mass = user_initial_mass
        self.cmd_grabimage = "ffmpeg -y -i %s -vframes 1 -ss 00:00:02 -an -vcodec png -f rawvideo -s 320x240 %s "
        self.TaskList = []
    
    def init_task(self):
        if not os.path.exists(self.src_path):
            print "src path [%s] not exists!" % self.src_path
            return
        
        if not os.path.exists(self.dst_path):
            print "Not exists dst path [%s] Now Create" % self.dst_path
            os.makedirs(self.dst_path)
        for root, dirs, files in os.walk(self.src_path):
            for video_file in files:
                if video_file.lower().endswith(_CODE_EXISTS):
                    video = os.path.join(root, video_file)
                    self.TaskList.append(video)
                    #test
                    #print "Find Video File [%s]" % video
    
    def time_seek(self, t1="01:50:12"):
        t = map(lambda x: int(x), t1.split(":"))
        t[1] = t[1] + self.SPLIT_TIME
        if t[1] >= 60:
            t[0] = t[0] + 1
            t[1] = t[1] - 60
        return ":".join(map(lambda x:"%02d" % x, t))
        
        
    def main(self):
        self.init_task()
        for i in self.TaskList:
            try:
                get_time_cmd = '"mplayer -identify %s -nosound -vc dummy -vo null|findstr "ID_LENGTH"' % i
                try:
                    get_time_str = os.popen(get_time_cmd).read()
                    video_length = int(float(get_time_str.split("=")[-1].strip()))
                except:
                    print "get %s video_length Failed" % i
                    continue
                tstart = '00:00:00'
                count = 1
                TF = False
                if video_length <= self.SPLIT_TIME*60:
                    TF = True
                while 1:
                    try:
                        dst = os.path.join(self.dst_path, "%s%s.flv" % \
                                (os.path.basename(i).rsplit(".", 1)[0], '_%d' % count))
                        cmds = ['ffmpeg -i "%s" -y -qscale 6' % i]
                        if not TF:
                            cmds.append('-ss %s -t 00:%d:00 -ab 64 -ar 22050' % (tstart, self.SPLIT_TIME))
                        else:
                            cmds.append('-ss 00:00:00 -ab 64 -ar 22050')
                        if self.user_initial_mass:
                            cmds.append("-sameq")
                        cmds.append('-b %sK' % self._CODE_RATE)
                        cmds.append('-s 320x240 "%s"' % dst)
                        cmdline = ' '.join(cmds)
                        black_info = "File Seek: %s" % tstart
                        tstart = self.time_seek(tstart)
                        #test
                        #print cmdline
                        print "infile : %s" % i
                        print "outfile: %s" % dst
                        print black_info
                        ticker = Ticker()
                        print "[START]",
                        threading.Thread(target=ticker.run).start()
                        t_start = time.time()
                        sti, sto = os.popen4(cmdline)
                        contents = [ x for x in sto.read().split( "\n" ) if "Duration" in x ]
                        if not contents:
                            print u"Help! Get Vedio %s Infos Failed!" % i
                        ticker.tick = False
                        hrs, min, sec = time_reg.findall( contents[ 0 ] )[ 0 ]
                        print u"\nUSE TIME: %s" % time.strftime("%H:%M:%S", time.gmtime(time.time() - t_start))
                        print u"FLV Time  : %-10d seconds" % (float( sec ) + float( min ) * 60 + float( hrs ) * 3600 ,)
                        print "-"*80
                        if TF:
                            break
                        vt = tstart.split(":")
                        VT = int(vt[0])*3600 + int(vt[1])*60 + int(vt[2])                        
                        if VT >= video_length:
                            break                        
                        count += 1                 
                    except:break
            except Exception, e:
                print str(e)
        
if __name__ == '__main__':
    print '*********************************'
    print '  Copyright (C) video.artxun.com'
    print '  Author: ghostwwl'
    print '  Email: ghostwwl@gmail.com'
    print '*********************************\n'
    if len(sys.argv) < 3:
        print "UseAge: ff.exe src_path dst_path code_rate split_time user_initial_mass"
        print u"src_path          视频文件存放路径"
        print u"dst_path          转换后的视频存放路径"
        print u"code_rate         视频编码比特率 默认320k"
        print u"split_time        大视频按多长时间切分 默认60分钟 一般不用改"
        print u"user_initial_mass 是否使用原始质量转换 默认不使用 一般不用 不然文件大"
        print "\n"
        os.system("pause")
    else:
        src = sys.argv[1]
        dst = sys.argv[2]
        T = None
        if len(sys.argv) == 3:
            T = Conver_Flv(src, dst)
        elif len(sys.argv) == 4:
            code_rate = sys.argv[3]
            T = Conver_Flv(src, dst, code_rate)
        elif len(sys.argv) == 5:
            code_rate = sys.argv[3]
            split_time = int(sys.argv[4].strip())
            T = Conver_Flv(src, dst, code_rate, split_time)
        elif len(sys.argv) == 6:
            code_rate = sys.argv[3]
            split_time = int(sys.argv[4].strip())
            user_ima = sys.argv[5].strip()
            if 'y' in user_ima.lower():
                user_ima = True
            else:
                user_ima = False
            T = Conver_Flv(src, dst, code_rate, split_time, user_ima) 
        if T is not None:
            T.main()
        else:
            print "Not Find Engine"
        
    
