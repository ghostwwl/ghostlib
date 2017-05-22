#!/usr/bin/env python
#-*- coding: UTF-8 -*-

#********************************************
#   FileName: VirtualFileSystem.py
#   Note: The Memory VirturlFileSystem mode
#         Save The small file in Memory
#   Author: wule
#   Date: 2007-10-11
#   Email: ghostwwl@gmail.com
#********************************************

from math import ceil
import time
import md5
import sys
import os
import zipfile
from os.path import basename, dirname
from memblack import MemBlack
from threading import Lock

class MemFileSystem(object):
    '''
    size 虚拟文件内存catch的大小 默认100MB 
    pagesize 虚拟文件分页大小 默认16KB
    path 虚拟文件在物理磁盘的路径，所有的虚拟文件都会以这个路径为根目录
    '''
    def __init__(self, size = 100, pagesize = 16, path = "/", errapi = None, debug = 1):
        self.RootPath = path
        self.MemBlackSize = size   
        self.MemPageSize = pagesize
        self.UseSize = 0.0
        self.FreeSize = float(self.MemBlackSize)
        self.Debug = debug
        if not self.debug:
            try:
                self.LogFile = open(os.path.join(self.FilePath, 'Error.log'), "ab+")
            except:
                self.Debug = 1
        self.BlackNum = ceil(float(1024*size/self.MemPageSize))
        self.FreeBlackNum = self.BlackNum
        self.FreeBlackList = list(range(self.BlackNum))
        try:
            self.Black = MemBlack(self.MemBlackSize, self.MemPageSize)
        except Exception, err:
            self.debuginfo(str(err))
            sys.exit(0)
        self.BlackPageTable = {}
        self.FileTableLock = Lock()
        self.FileTable = {}
        self.DirectorTable = {}
        self.DirectorTableLock = Lock()
        self.init_filesystem()
        if errapi:
            self.debuginfo = errapi
        else:
            self.debuginfo = self.debugio
        
    def init_balck(self):
        '''
        初始化分页块
        '''
        for i in range(self.BlackNum):
            self.BlackPageTable[i] = dict([('isfull', False),('bytes', 0),
            ('offset', i*self.MemPageSize*1024)])
    
    def mk_dirs(self, director):
        '''
        director 需要初始化的目录
        所有目录逻辑结构上构成n层多叉树
        目录是线性目录--->子母不能递归包含父目录
        '''
        #dirs = [i.strip() for i in director.split("/")[1:] if i]
        try:
            head, tail = os.path.split(director)
            if not tail:
                #有可能在结尾有路径分隔符
                head, tail = os.path.split(head)
                if head == self.RootPath and not tail:
                    return 1
            pstr = head
            if head == self.RootPath:
                #在根目录下创建目录
                pstr = pstr  + tail
            else:
                pstr = pstr + '/' + tail
            self.DirectorTable[pstr] = dirc([('dir_name',tail), ('isEmpty', True),
            ('file_list',[]), ('parent_dir', head),('create_time', self.time_now()),('child_dir',[])])
            
            if self.DirectorTable.has_key(head):
                self.DirectorTable[head]['child_dir'].append(pstr)
                self.DirectorTable[head]['isEmpty'] = False

            if head and tail and not self.DirectorTable.has_key(head):
                self.mk_dirs(head)
        except Exception, err:
            self.debuginfo("OSError: [Errno 17] File exists: %s" % self.RootPath)
            return -1
            
    def ls(self, mfile, recursive = False):
        mf = self.FileTable.get(md5.new(mfile).digest(), None)
        mdir = self.FileTable.get(mfile, None)
        result = []
        try:
            if mf:
                result.append([mf['create_time'], mf["filesize"], os.path.basename(mf['filename'])])
            if mdir:
                result.append([mdir['create_time'], 'DIR', mdir['dir_name']])
                if mdir['file_list']:
                    for i in mdir['file_list']:
                        r = self.ls(i, recursive)
                        result.append(r)
                if mdir['child_dir']:
                    for i in mdir['child_dir']:
                        r = self.ls(i, recursive)
                        result.append(r)
                return result
            if not mf and not mdir:
                raise Exception("OError: [Errno 2] No such file or directory: %s" % mfile)
        except Exception, err:
            self.debuginfo("ls command Error: %s" % str(err))
        return result
        
    def init_filesystem(self):
        '''
        初始化文件系统 创建根目录
        '''
        try:
            self.DirectorTable[self.RootPath] = dict([("dir_name", self.RootPath),("isEmpty",True),
            ("file_list",[]),("parent_dir",None),('create_time', self.time_now()), ("child_dir",[])])
            self.init_balck()
        except Exception, err:
            self.debuginfo(str(err))
            sys.exit(0)
            
    def pre_data(self, f, flg):
        '''
        这个还要修改，要把文件逻辑分类到其完整路径的指定路径下
        f 为需要写入的文件
        flg 目标文件存在时 是否覆盖
        '''
        self.FileTableLock.acquire()
        self.DirectorTableLock.acquire()
        try:
            dirs = os.path.dirname(f)
            md5str = md5.new(f).digest()
            if flg and self.FileTable.has_key(md5str):
                #文件存在并且要覆盖的情况 对原来的页释放
                for i in self.FileTable[md5str]['index']:
                    pageinfo = self.BlackPageTable.get(i)
                    self.Black.reuse(pageinfo['offset'], pageinfo['bytes'])
                    pageinfo['isfull'] = False
                    self.FreeBlackList.append(i)
                    self.FreeBlackNum += 1
                self.FreeBlackList.sort()
                del self.FileTable[md5str]
            #文件不存在的情况
            self.FileTable[md5str] = dict([("filename", f),("filesize", 0),
            ('create_time', self.time_now())("offset", 0),("index", [])])
            if not self.DirectorTable.has_key(dirs):
                self.mk_dirs(dirs)
            self.DirectorTable[dirs]['file_list'].append(md5str)
            if not flg and self.FileTable.has_key(md5str):
                raise Exception("OSError: [Errno 17] File exists: %s" % f)
        except Exception, err:
            self.debuginfo(str(err))
        self.FileTableLock.release()
        self.DirectorTableLock.release()
        return md5str
    
    def write(self, filename, data, replace = False):
        '''
        写失败的时候要回收内存资源 返回 -1
        写成功 返回文件的 字节数
        '''
        ret_flg = -1
        try:
            id = self.pre_data(filename, replace)
            writel = len(data)
            self.FileTable[id]['filesize'] = writel
            dat = data[:1024*self.MemPageSize]
            data = data[1024*self.MemPageSize:]
        except Exception, err:
            self.debuginfo(str(err))
            return -1
        self.FileTableLock.acquire()
        self.DirectorTableLock.acquire()
        while dat:
            try:
                if self.FreeBlackList:
                    page = self.FreeBlackList.pop(0)
                else:
                    raise Exception("MemBlack is full!")
                flg = self.Black.write(self.BlackPageTable[page]['offset'], dat)
                if flg < 0:
                    raise Exception("Write Error!")
                self.BlackPageTable[page]['isfull'] = True
                self.BlackPageTable[page]['bytes'] = len(dat)
                self.FileTable[id]['index'].append(page)
                dat = data[:1024*self.MemPageSize]
                data = data[1024*self.MemPageSize:]
                self.FreeBlackNum -= 1
                flg = 1
            except IOError, err:
                #写失败 对已经写成功的页回收
                try:
                    dirs = os.path.dir(filename)
                    mdr = self.DirectorTable.get(dirs, None)
                    id = md5.new(filename)
                    if mdr:
                        del mdr["file_list"][mdr["file_list"].index(id)]
                    self.BlackPageTable[page]['isfull'] = False
                    self.FreeBlackList.append(page)
                    self.FreeBlackNum += 1
                    for i in self.FileTable[id]['index']:
                        self.Black.reuse(self.BlackPageTable[i]['offset'])
                        self.BlackPageTable[i]['isfull'] = False
                        self.FreeBlackList.append(i)
                        self.FreeBlackNum += 1
                    self.FreeBlackList.sort()
                    del self.FileTable[id]
                except:
                    self.debuginfo("write file %s error: %s" % (filename, str(err)))
                flg = -1
                break
        self.FileTableLock.release()
        self.DirectorTableLock.release()
        if flg > 0:
            flg = len(data)
        return flg
                
    def read(self, filename, byte, flg = True):
        '''
        byte 需要读取的字节数 默认是读取整个文件
        flg 读取文件,读完后是否释放虚拟页 默认读完后释放虚拟页
        '''
        id = md5.new(filename).digest()
        dat = ''
        self.FileTableLock.acquire()
        try:
            if self.FileTable.has_key(id):
                fileinfo = self.FileTable.get(id)
                n = ceil(byte/(self.MemBlackSize*1024.0)) 
                if  0 < n < len(fileinfo['index']):
                    for k in fileinfo['index'][:n]:
                        pageinfo = self.BlackPageTable.get(k)
                        dat += self.Black.read(pageinfo['offset'], pageinfo['bytes'])
                        if flg:
                            self.Black.reuse(pageinfo['offset'], pageinfo['bytes'])
                            del self.FileTable[id]
                            dirs = os.path.dirname(filename)
                            dirinfo = self.DirectorTable.get(dirs, None)
                            del dirinfo["file_list"][dirinfo["file_list"].index(id)]
                            pageinfo['isfull'] = False
                            self.FreeBlackList.append(k)
                            self.FreeBlackNum += 1
                else: 
                    for i in self.FileTable[id]['pageindex']:
                        pageinfo = self.BlackPageTable.get(i)
                        dat += self.Black.read(pageinfo['offset'], pageinfo['bytes'])
                        if flg:
                            self.Black.reuse(pageinfo['offset'], pageinfo['bytes'])
                            pageinfo['isfull'] = False
                            self.FreeBlackList.append(i)
                            self.FreeBlackNum += 1
                self.FreeBlackList.sort()
        except Exception, err:
            self.debuginfo("%s No such file or directory: %s" % (str(err), filename))
        self.FileTableLock.release()
        return dat
    
    def del_file(self, filename):
        '''
        删除文件
        '''
        id = md5.new(filename).digest()
        try:
            if self.FileTable.has_key(id):
                for i in self.FileTable[id]['index']:
                    pageinfo = self.BlackPageTable.get(i)
                    self.Black.reuse(pageinfo['offset'], pageinfo['bytes'])
                    pageinfo['isfull'] = False
                    self.FreeBlackList.append(i)
                    self.FreeBlackNum += 1
                dirs = os.path.dirname(filename)
                rf = self.DirectorTable.get(dirs, None)
                if rf:
                    del rf["file_list"][rf["file_list"].index(id)]
            return 1
            
        except Exception, err:
            self.debuginfo("No such file or directory: %s" % filename)
        return -1
           
    def del_dir(self, dir):
        '''
        删除目录
        '''
        try:
            head, tail = os.path.split(dir)
            dirs = head
            if tail:
                dirs += tail
            rmdir = self.DirectorTable.get(dirs, None)
            if rmdir:
                child_dirs = rmdir.get('child_dir', None)
                if child_dirs:
                    for i in child_dirs:
                        self.del_dir(i)
                    del i
                file_list = rmdir.get('file_list', None)
                if file_list:
                    for j in file_list:
                        self.del_file(j)
                    del j
                return 1
            else:
                raise Exception("No such file or directory: %s" % dir)
        except Exception, err:
            self.debuginfo(str(err))
            return -1
        
    def rm(self, path_or_file):
        '''
        通用删除接口
        '''
        try:
            f = self.Attribute(path_or_file)
            if f == 1:
                self.del_file(path_or_file)
            if f == 2:
                self.del_dir(path_or_file)
            return 1
        except Exception, err:
            self.debuginfo(str(err))
            return -1
    
    def Attribute(self, file_or_dir):
        '''
        文件类型查看接口
        '''
        try:
            file_or_dir = file_or_dir.strip()
            if self.DirectorTable.has_key(file_or_dir):
                return 2
            if self.FileTable.has_key(md5.new(file_or_dir).digest()):
                return 1
            return 0
        except Exception, err:
            self.debuginfo(str(err))
            return -1
        
    def import_path(self, sname, dname, recursive = True, replace = True):
        '''
        sname:源目录或Zip文件
        dname:目标目录
        recursive:是否包含子目录
        replace:目标存在时是否覆盖
        '''
        dname = dname.strip()
        dname = dname.replace("/", os.sep)
        dname = dname.replace("\\", os.sep)            
        if not dname.endswith(os.sep):
            dname += os.sep
        if os.path.isfile(sname):
            #如果导入的源文件是一个zip文件
            try:
                iszipfile = zipfile.is_zipfile(sname)
                if iszipfile:
                    zip = zipfile.ZipFile(zip, 'r', zipfile.ZIP_DEFLATED)    
                for src in zip.NameToInfo.keys():
                    if src.endswith('/'):
                        continue
                    srcfile = dname + src
                    srcfile = os.path.abspath(srcfile)
                    srcpath = os.path.dirname(srcfile)
#                    if not os.path.exists(srcpath):
#                        os.makedirs(srcpath)
                    zzip = zipfile.ZipFile(zip, 'r', zipfile.ZIP_DEFLATED)(zip, src, srcfile)
                    if srcfile:
                        try:
                            self.write(srcfile, zzip.read(src), replace)
                        except:
                            pass
                        zzip.close()
                if iszipfile:
                    zip.close()
                return 1
            except Exception, err:
                self.debuginfo(str(err))
                return -1
            
        if os.path.isdir(sname):
            #如果导入的文件是一个目录
            try:
                for i in os.listdir(sname):
                    file_or_dir = os.path.join(sname, i)
                    if os.path.isfile(i):
                        try:
                            f = open(i, "rb")
                            dat = f.read()
                            f.close()
                            dst_file = dname + i
                            self.write(dst_file, dat, replace)
                        except:
                            pass
                    if recursive and os.path.isdir(file_or_dir):
                        self.import_path(file_or_dir)
                return 1
            except Exception, err:
                self.debuginfo(str(err))
                return -1
        
        if not os.path.isfile(sname) and not os.path.isdir(sname):
            self.debuginfo("import_path Error: %s not a zipfile and not a path" % sname)
            return -1
                    
    
    def export_path(self, sname, dname, recursive = True):
        '''
        sname:源目录
        dname:目标目录或Zip文件
        recursive:是否包含子目录
        '''
        zipflg = False
        sname = sname.strip()
        try:
            if dname.endswith(".zip") or dname.endswith(".gz"):
                zipflg = True
                if os.path.exists("dname"):
                    zfile = zipfile.ZipFile(dname, 'a', zipfile.ZIP_DEFLATED)
                else:
                    zfile = zipfile.ZipFile(dname, 'w', zipfile.ZIP_DEFLATED)

            if self.DirectorTable.has_key(sname):
                DirIndex = self.DirectorTable.get(sname, None)
                if DirIndex:
                    for i in DirIndex['file_list']:
                        
                        if zipflg:
                            dfile = os.path.join('', i)
                            
                    for i in DirIndex['child_dir']:
                        pass
                else:
                    raise Exception("Get directory %s Index Error" % sname)
                return 1
            else:
                raise Exception("No such directory %s" % sname)
        except Exception, err:
            self.debuginfo(str(err))
            return -1
        
        def zip_path(zip, path, opppath = ''):
            '''Zip all the files of path, return None'''
            if os.path.exists(zip):
                zip = zipfile.ZipFile(zip, 'a', zipfile.ZIP_DEFLATED)
            else:
                zip = zipfile.ZipFile(zip, 'w', zipfile.ZIP_DEFLATED)
            for src in os.listdir(path):
                srcfile = os.path.join(path, src)
                oppfile = os.path.join(opppath, src)
                if os.path.isfile(srcfile):
                    zip.write(srcfile, oppfile)
                elif os.path.isdir(srcfile):
                    zip_path(zip, srcfile + os.sep, oppfile + os.sep)
            if not iszipfile:
                zip.close()
                
    
    def mem_black_info(self):
        result = {}
        try:
            self.FreeSize = self.FreeBlackNum*1024.0
            self.UseSize = (self.BlackNum - self.FreeBlackNum)*1024.0
            result['FreeSize'] = self.FreeSize
            result['UseSize'] = self.UseSize
        except Exception, err:
            self.debuginfo(str(err))
        return result
    
    def mount(self, mountpoint):
        '''
        挂载接口
        '''
        pass
        
    def free_memblack(self):
        '''
        释放所有的虚拟页
        '''
        try:
            self.UseSize = 0.0
            self.FreeSize = 100.0
            self.BlackNum = ceil(float(1024*size/self.MemPageSize))
            self.FreeBlackNum = self.BlackNum
            self.FreeBlackList = list(range(self.BlackNum))        
            for i in range(self.BlackNum):
                self.Black[i]['data'].reuse()
                self.Black[i]['isfull'] = False
            return 1
        except Exception, err:
            self.debuginfo(str(err))
            return -1
    
    def time_now(self):
        return time.strftime("%Y-%m-%d %H:%M:%S")
    
    def debugio(self, info):
        info = "%s --> %s\n" % (self.time_now(), info)
        if self.Debug:
            print info
        else:
            self.LogFile.write(info)
            self.LogFile.flush()
        
        
if __name__ == '__main__':
    test()
