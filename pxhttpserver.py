#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#********************************
# pxhttpserver:
#     轻量级的HTTP服务器
# author:
#     zhangcheng
# version:
#     1.0（2007-07-27）
#     1.1（2007年09月13日）
#       增加了一组网页转换函数
#     1.2（2007年10月12日）
#       支持打开本地和远程页面
#     1.3（2007年10月16日）
#       命令解析时，去除扩展名
#********************************

import BaseHTTPServer, SimpleHTTPServer
import threading, urllib, urllib2, socket, urlparse
import os, time, sys, re

version = '1.3'
CON_DEFAULT_HOMEPAGE = '/test'
CON_DEFAULT_ROOT = 'local'

# 下载一个资源
def sys_download(url, dat = '', mode = 'Post', proxy = None, refer = None):
    try:
        tfile = None
        if mode == 'Post':
            request = urllib2.Request(url, dat)
        elif mode == 'Get':
            request = urllib2.Request(url)
        else:
            return(False, 'Error command mode.')
        request.add_header('Pragma', 'no-cache')
        request.add_header('Cache-Control', 'no-cache')
        request.add_header('Accept', '*/*')
        request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; SV1; .NET CLR 1.1.4322)')
        if refer:
            request.add_header('Referer', refer)
        if proxy:
            request.set_proxy(proxy, 'http')
        opener = urllib2.build_opener()
        tfile = opener.open(request)
        ret = tfile.read()
        result = True
    except Exception, args:
        ret = 'Download %s error.(%s)' % (url, str(args))
        result = False
    if tfile:
        tfile.close()
    return (result, ret)

# 解析参数
def sys_parse_param(inStr, outDict):
    '''Parse inStr to outDict'''
    inStr = inStr.replace('+','%20').strip()
    L = inStr.split('&')
    for s in L:
        i = s.find('=')
        k = s[:i]
        v = urllib.unquote(s[i+1:])
        if k:
            outDict[k] = v

# 构造参数
def sys_build_param(inDict):
    '''Build a inDict to param data'''
    L = []
    for k,v in inDict.items():
        s = str(k) + '=' + urllib.quote(str(v),'')
        s = s.replace('+','%20')
        L.append(s)
    return '&'.join(L)

# 以下是一组网页转换函数
def sys_quote_html(html):
    return html.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def sys_unquote_html(html):
    return html.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&")

def sys_quote_xml(xml):
    return xml.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&apos;").replace('"', "&quot;")

def sys_unquote_xml(xml):
    return xml.replace("&apos;", "'").replace("&quot;", '"').replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&")

# HTTP处理器类
class Http_Manage_Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, request, client_address, server)
    
    def log_message(self, format, *args):
        pass # 屏蔽提示消息

    def get_cmd(self, p):
        if p == '/':
            p = CON_DEFAULT_HOMEPAGE # 使用默认主页
        urllist = urlparse.urlparse(p)
        dirlist = urllist[2].split('/')
        if len(dirlist) <= 2:
            driver = ''
        else:
            driver = dirlist[1]
        path = os.sep.join(dirlist[2:-1])
        fname = dirlist[-1]
        param = {}
        sys_parse_param(urllist[4], param) 
        return (driver, path, fname, param)
    
    def get_file(self, driver, path, fname, param):
        try:
            root = os.path.dirname(sys.argv[0])
            redirfile = os.path.join(root, driver, 'redir.txt')
            if os.path.exists(redirfile):
                # 通过调用重定向数据获取返回数据
                f = open(redirfile, 'rb')
                redirurl = f.readline()
                f.close()
                if path:
                    url = urlparse.urljoin(redirurl, path.replace('\\','/') + '/' + fname)
                else:
                    url = urlparse.urljoin(redirurl, fname)
                if param:
                    url += '?' + sys_build_param(param) # 如果带参数，可能顺序会不一样
                result, ret = sys_download(url, mode = 'Get')
                # 需要替换绝对路径           
                if result and driver:
                    ret = re.sub('(\s(?:action|href|src)\s*?=\s*?(?:[\'|"]?)\s*?/)', '\\1%s/' % driver, ret)
            else:
                # 读取本地文件并返回
                if driver == '':
                    driver = CON_DEFAULT_ROOT
                elif not os.path.exists(os.path.join(root, driver)):
                    driver = CON_DEFAULT_ROOT + os.sep + driver
                f = open(os.path.join(root, driver, path, fname), 'rb')
                ret = f.read()
                f.close()
                result = True
        except Exception, args:                
            ret = 'Can not handle the get command: %s.(%s)' % (fname, str(args))
            result = False
        return (result, ret)
    
    def post_file(self, driver, path, fname, param):
        try:
            root = os.path.dirname(sys.argv[0])
            redirfile = os.path.join(root, driver, 'redir.txt')
            if os.path.exists(redirfile):
                # 通过调用重定向数据获取返回数据
                f = open(redirfile, 'rb')
                redirurl = f.readline()
                f.close()
                if path:
                    url = urlparse.urljoin(redirurl, path.replace('\\','/') + '/' + fname)
                else:
                    url = urlparse.urljoin(redirurl, fname)
                result, ret = sys_download(url, sys_build_param(param), 'Post')
                # 需要替换绝对路径                
                if result and driver:
                    ret = re.sub('(\s(?:action|href|src)\s*?=\s*?(?:[\'|"]?)\s*?/)', '\\1%s/' % driver, ret)
            else:
                # 读取本地文件并返回
                if driver == '':
                    driver = CON_DEFAULT_ROOT
                elif not os.path.exists(os.path.join(root, driver)):
                    driver = CON_DEFAULT_ROOT + os.sep + driver
                f = open(os.path.join(root, driver, path, fname), 'rb')
                ret = f.read()
                f.close()
                result = True
        except Exception, args:                
            ret = 'Can not handle the post command: %s.(%s)' % (fname, str(args))
            result = False
        return (result, ret)

    # 获得Get请求
    def do_GET(self):
        driver, path, fname, param = self.get_cmd(self.path.strip()) # 解析参数        
        mainobj = self.server.parent.parent # 设置主线程中的对象
        cmd = 'cmd_' + re.sub('\.[^\.]*?$', '', fname).lower()
        if (driver == '') and (hasattr(mainobj, cmd)):
            method = getattr(mainobj, cmd)
            try:
                ret = method(param) # 执行本地请求
                result = True
            except Exception, args:                
                ret = 'Can not handle the get command: %s.(%s)' % (cmd, str(args))
                result = False
        else: # 执行本地文件或执行外部请求
            result, ret = self.get_file(driver, path, fname, param)
        if result:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(ret)
        else:
            self.send_error(501, ret)
                
    # 获得Post请求
    def do_POST(self):
        driver, path, fname, param = self.get_cmd(self.path.strip()) # 解析参数
        self.rfile._sock.settimeout(1) # 读入所有请求的数据
        pl = []
        while True:
            try:
                ch = self.rfile.read(1)
            except:
                break
            pl.append(ch)
            pl.append(self.rfile.read(len(self.rfile._rbuf)))
        sys_parse_param(''.join(pl), param) # 解析Post的数据        
        mainobj = self.server.parent.parent # 设置主线程中的对象
        cmd = 'cmd_' + re.sub('\.[^\.]*?$', '', fname).lower()
        if (driver == '') and (hasattr(mainobj, cmd)):
            method = getattr(mainobj, cmd)
            try:
                ret = method(param) # 执行本地请求
                result = True
            except Exception, args:               
                ret = 'Can not handle the post command: %s.(%s)' % (cmd, str(args))
                result = False
        else: # 执行本地文件或执行外部请求
            result, ret = self.post_file(driver, path, fname, param)
        if result:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(ret)
        else:
            self.send_error(502, ret)

# Http服务器（重载若干方法）
class Http_Manage_Server(BaseHTTPServer.HTTPServer):
    '''Defin the manage server'''
    def __init__(self, server_address, RequestHandlerClass, parent):
        self.parent = parent
        self.allow_reuse_address = 0 # 禁止地址复用
        self.request_queue_size = 50 # 请求队列的长度
        BaseHTTPServer.HTTPServer.__init__(self, server_address, RequestHandlerClass)
        
    def get_request(self):
        # 重载获取一个请求，获取到一个请求后，即再生成一个处理线程
        try:
            ret = BaseHTTPServer.HTTPServer.get_request(self)
        except Exception, args:
            self.parent.CreateManageThread()
            raise Exception(str(args))
        self.parent.CreateManageThread()
        return ret

    def close_request(self, request):
        """Called to clean up an individual request."""
        # 这个地方原本想用来清理链接的遗留信息，就是断开到服务器的链接
        # 过多的等待断开的链接会导致将网卡冲死
        # 这个问题还没有解决，期待高手...
        #print dir(request._sock)
        #print request._sock.__doc__
        request.close()
        #request = None
        #self.socket.close()

    def handle_error(self, request, client_address):
        """Handle an error gracefully.  May be overridden.

        The default is to print a traceback and continue.

        """
        pass

# HTTP服务线程
class Http_Manage_Thread(threading.Thread):
    def __init__(self, threadname, parent):
        threading.Thread.__init__(self, name = threadname)
        self.parent = parent

    def run(self):
        self.parent.httpserver.handle_request() # 处理请求

# HTTP服务设备类
class Http_Manage_Device:
    def __init__(self, parent, port, threadcount = 20, bindip = ''):
        self.parent = parent # 处理类
        self.threadid = 0
        try:            
            self.httpserver = Http_Manage_Server((bindip,port), Http_Manage_Handler, self) # 绑定端口
            self.state = 'Pylynx http server %s is OK, listening port %d.' % (version, port)
        except Exception, args:
            self.httpserver = None # 绑定失败后，httpserver为空
            self.state = 'Can not open http server.(%s)' % str(args)
            return
        for i in xrange(threadcount):
            self.CreateManageThread()
            time.sleep(0.1)
    
    # 创建处理线程        
    def CreateManageThread(self):
        self.threadid += 1
        mt = Http_Manage_Thread('manage_thread_%d' % self.threadid, self)
        mt.setDaemon(True)
        mt.start()

class TestClass:
    def __init__(self):
        self.Terminated = False
        
    def cmd_main(self, param):
        return 'Welcome'
    
    def cmd_test(self, param):
        info = param['info']
        return info
    
    def cmd_exit(self, param):
        passwd = param['passwd']
        if passwd == 'woyaofeidegenggao':
            self.Terminated = True
            return 'bye-bye'

if __name__ == '__main__':
    t = TestClass()
    c = Http_Manage_Device(t, 50001, 20)
    print c.state
    if c.httpserver:
        while not t.Terminated:
            time.sleep(0.01)
