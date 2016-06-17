#!/usr/bin/env python
#-*- coding:utf-8 -*-

#***********************************
#  Author: ghostwwl
#  DateTime: 2008.2
#  Email: ghostwwl@gmail.com
#  2008.6.25 取消自动referer
#***********************************

import urllib2
import urllib
import cookielib
import socket
import mimetypes
from gzip import GzipFile
from StringIO import StringIO

_version_ = '1.0'
_author_ = 'ghostwwl'
_email_ = 'ghostwwl@gmail.com'
 
class GRequest(object):
    USER_ANGEN = 'Mozilla/5.0 (Windows NT 5.2; rv:12.0) Gecko/20100101 Firefox/12.0'
    def __init__(self, proxy = None, TimeOut = 120):
        '''
        proxy:  all request use this proxy only http proxy default None
        TimeOut: set the socket's setdefaulttimeout
        '''
        socket.setdefaulttimeout(TimeOut)
        self.cookies = urllib2.HTTPCookieProcessor(cookielib.CookieJar())
        self.proxy = proxy
    
    def clear_cookie(self):
        '''clear the cookie'''
        del self.cookies
        self.cookies = urllib2.HTTPCookieProcessor(cookielib.CookieJar())
        return True
        
    def set_proxy(self, proxy = None):
        if proxy is not None:
            self.proxy = proxy
            return True
        
    def set_timeout(self, TimeOut = 120):
        socket.setdefaulttimeout(TimeOut)
        return True
    
    def request_url(self, url, dat=None, **headers):
        try:
            result = False
            SockFile = None
            if dat:
                request = urllib2.Request(url, dat)
            else:
                request = urllib2.Request(url)
            request.add_header('User-Agent', self.USER_ANGEN)
            request.add_header('Pragma', 'no-cache')
            request.add_header('Cache-Control', 'no-cache')
            if headers:
                #headers -- other request header
                for k, v in headers.items():
                    request.add_header(str(k), str(v))
            if self.proxy:
                request.set_proxy(self.proxy, 'http')
            opener = urllib2.build_opener(self.cookies)
            SockFile = opener.open(request)
            ret = SockFile.read()
            result = True
        except Exception, e:
            ret = 'Open %s Error: %s' % (str(url), str(e))
        if SockFile:
            SockFile.close()
        return (result, ret)
    
    def init_table(self, inDat, TheEncode = 'GB2312', space=True):
        '''encode frame table for http post
        
        inDat The frame data dict type
        TheEncode post page encode
        space     replace space to %20 if True else +'''
        return self.encode_table(inDat, TheEncode, space)
    
    @staticmethod
    def encode_table(inDat, TheEncode = 'GB2312', space=True):
        '''encode frame table for http post
        
        inDat The frame data dict type
        TheEncode post page encode
        space     replace space to %20 if True else +'''
        L = []
        for k, v in inDat.items():
            v = str(v)
            v = unicode(v, 'utf-8')
            v = v.encode(TheEncode, 'ignore')
            s = str(k) + '=' + urllib.quote(v,'')
            if space:
                s = s.replace('+','%20')
            L.append(s)
        return '&'.join(L)
    
    @staticmethod
    def encode_multipart(fields, files=None, BOUNDARY=None):
        """fields 需要编码的frame的字段和值组成的元组的列表
        files 是字段名， 文件名 组成的列表
        """
        if not BOUNDARY:
            BOUNDARY = '---------------------------7d92fd32c0660'
        #BOUNDARY = mimetools.choose_boundary()
        CRLF = '\r\n'
        L = []
        for (key, value) in fields:
            L.append('--%s' % str(BOUNDARY))
            L.append('Content-Disposition: form-data; name="%s"' % str(key))
            L.append('')
            L.append(str(value))
        if files:
            for (key, filename) in files:
                value = ''
                try:
                    f = open(filename, 'rb')
                    value = f.read()
                    f.close()
                except:continue
                if value:
                    L.append('--%s' % str(BOUNDARY))
                    L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
                    filetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
                    L.append('Content-Type: %s' % filetype)
                    L.append('')
                    L.append(value)
        L.append('--%s--' % str(BOUNDARY))
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, body
    
#-------------------------------------------------------------------------------
#这个基本很少用到 除非要不停的切换USER_ANGEN
USER_ANGENS = (
'Mozilla/4.0 (compatible; MSIE 7.0; America Online Browser 1.1; rev1.2; Windows NT 5.1; SV1; .NET CLR 1.1.4322)', 
'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6 (Change: )', 
'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en; rv:1.9.0.10pre) Gecko/2009041800 Camino/2.0b3pre (like Firefox/3.0.10pre)', 
'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; Avant Browser; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)', 
'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.5) Gecko/20031007 Firebird/0.7', 
'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser; .NET CLR 2.0.50727; MAXTHON 2.0)', 
'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_0; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.202.0 Safari/532.0', 
'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Avant Browser; Avant Browser; .NET CLR 2.0.50727)', 
'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; GTB5; Avant Browser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)', 
'Mozilla/5.0 (compatible; U; ABrowse 0.6; Syllable) AppleWebKit/420+ (KHTML, like Gecko)', 
'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/531.3 (KHTML, like Gecko) Chrome/3.0.193.2 Safari/531.3', 
'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Deepnet Explorer 1.5.3; Smart 2x2; .NET CLR 2.0.50727; .NET CLR 1.1.4322; InfoPath.1)', 
'Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.1; AOLBuild 4334.5006; Windows NT 5.1; Trident/4.0; DigExt; .NET CLR 1.1.4322)', 
'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1b5pre) Gecko/20090428 SeaMonkey/2.0b1pre', 
'Mozilla/5.0 (Windows; Windows NT 5.1; en-US; rv:1.9.2a1pre) Gecko/20090402 Firefox/3.6a1pre', 
'Mozilla/5.0 (X11; U; Linux; fi-FI) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6 (Change: 754 46b659a)', 
'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/3.0.195.4 Safari/532.0', 
'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en; rv:1.9.0.8pre) Gecko/2009022800 Camino/2.0b3pre', 
'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/3.0.195.1 Safari/532.0', 
'Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.80; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)', 
'Mozilla/5.0 (Windows; U; Windows NT 5.1; ja; rv:1.9.2a1pre) Gecko/20090402 Firefox/3.6a1pre (.NET CLR 3.5.30729)', 
'Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:1.9.1b4pre) Gecko/20090419 SeaMonkey/2.0b1pre', 
'Mozilla/5.0 (Windows; U; WinNT; en; rv:1.0.2) Gecko/20030311 Beonex/0.8.2-stable', 
'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1b5pre) Gecko/20090517 Firefox/3.5b4pre (.NET CLR 3.5.30729)', 
'Mozilla/4.0 (compatible; MSIE 7.0; America Online Browser 1.1; rev1.5; Windows NT 5.1; .NET CLR 1.1.4322)', 
'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/530.8 (KHTML, like Gecko) Chrome/2.0.178.0 Safari/530.8', 
'Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.1; AOLBuild 4334.5006; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 1.0.3705; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)', 
'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6 (Change: )', 
'Mozilla/5.0 (X11; U; Linux; ru-RU) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6 (Change: 802 025a17d)',
'Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.81; Windows NT 6.0; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30618)',
'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-TW; rv:1.9.1.2) Gecko/20090729 Firefox/3.5.2',
'Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.93; Windows NT 5.1; Trident/4.0; DigExt; .NET CLR 1.1.4322)', 
'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en-US; rv:1.0.1) Gecko/20021111 Chimera/0.6', 
'Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.1; AOLBuild 4334.5006; Windows NT 5.1; GTB5; .NET CLR 1.1.4322; .NET CLR 2.0.50727)', 
'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1b2) Gecko/20060821 BonEcho/2.0b2', 
'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT; Avant Browser; Avant Browser; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2)', 
'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; WOW64; Avant Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; InfoPath.1; .NET CLR 3.5.30729; .NET CLR 3.0.30618)', 
'Mozilla/5.0 (Macintosh; U; PPC Mac OS X Mach-O; en-US; rv:1.0.1) Gecko/20030111 Chimera/0.6', 
'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/531.3 (KHTML, like Gecko) Chrome/3.0.193.0 Safari/531.3', 
'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.7) Gecko/20071018 BonEcho/2.0.0.7', 
'Mozilla/5.0 (Macintosh; U; Intel Mac OS X; en) AppleWebKit/418.9 (KHTML, like Gecko, Safari) Cheshire/1.0.UNOFFICIAL', 
'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser; .NET CLR 2.0.50727; .NET CLR 3.0.04506.590; .NET CLR 3.5.20706; Crazy Browser 2.0.1)', 
'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; Avant Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506; .NET CLR 3.5.21022; InfoPath.2)', 
'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; Avant Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506; .NET CLR 3.5.21022; InfoPath.2)', 
'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; Acoo Browser; GTB6; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; InfoPath.1; .NET CLR 3.5.30729; .NET CLR 3.0.30618)', 
'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; InfoPath.2; .NET CLR 2.0.50727; .NET CLR 1.1.4322; Crazy Browser 3.0.0 Beta2)', 
'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; pl-pl) AppleWebKit/312.8 (KHTML, like Gecko, Safari) DeskBrowse/1.0', 
'Mozilla/5.0 (X11; U; Linux i686 (x86_64); en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.202.2 Safari/532.0', 
'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/531.4 (KHTML, like Gecko) Chrome/3.0.194.0 Safari/531.4', 
'Mozilla/5.0 (BeOS; U; BeOS BePC; en-US; rv:1.8.1.7) Gecko/20070917 BonEcho/2.0.0.7', 
'Mozilla/5.0 (Windows; U; Windows NT 6.0; en; rv:1.9.1b4pre) Gecko/20090419 SeaMonkey/2.0b1pre', 
'Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.1; AOLBuild 4334.5006; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)', 
'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/3.0.195.1 Safari/532.0', 
'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/3.0.195.1 Safari/532.0', 
'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1b4pre) Gecko/20090401 Firefox/3.5b4pre', 
'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/531.3 (KHTML, like Gecko) Chrome/3.0.193.2 Safari/531.3', 
'Mozilla/5.0 (X11; U; Linux i686; nl; rv:1.8.1b2) Gecko/20060821 BonEcho/2.0b2 (Debian-1.99+2.0b2+dfsg-1)',
'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_7; en-US) AppleWebKit/531.3 (KHTML, like Gecko) Chrome/3.0.192 Safari/531.3', 
'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-GB; rv:1.9.1.2) Gecko/20090729 Firefox/3.5.2', 
'Mozilla/5.0 (Windows; U; Windows NT 6.0; de; rv:1.9.1.2) Gecko/20090729 Firefox/3.5.2', 
'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/531.2 (KHTML, like Gecko) Chrome/3.0.191.3 Safari/531.2', 
'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.6a) Gecko/20031002 Firebird/0.7', 
'Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.1; AOLBuild 4334.5000; Windows NT 5.1; Trident/4.0)', 
'Mozilla/5.0 (Windows; U; Windows NT 6.0; ru; rv:1.9.1b4pre) Gecko/20090419 SeaMonkey/2.0b1pre', 
'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en) AppleWebKit/418.8 (KHTML, like Gecko, Safari) Cheshire/1.0.UNOFFICIAL', 
'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/3.0.198.0 Safari/532.0', 
'Mozilla/5.0 (Windows; U; Windows NT 6.0; rv:1.9.1b4pre) Gecko/20090419 SeaMonkey/2.0b1pre', 
'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Deepnet Explorer 1.5.3; Smart 2x2; .NET CLR 1.1.4322; InfoPath.1; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)', 
'Mozilla/4.0 (compatible; MSIE 7.0; America Online Browser 1.1; rev1.5; Windows NT 5.1; .NET CLR 1.0.3705; .NET CLR 1.1.4322; Media Center PC 4.0; InfoPath.1; .NET CLR 2.0.50727; Media Center PC 3.0; InfoPath.2)', 
'Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.81; Windows NT 6.0; Trident/4.0; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30618)', 
'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/3.0.195.1 Safari/532.0', 
'Mozilla/4.0 (compatible; MSIE 8.0; AOL 9.5; AOLBuild 4337.43; Windows NT 6.0; Trident/4.0; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.5.21022; .NET CLR 3.5.30729; .NET CLR 3.0.30618)', 
'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; pl-PL; rv:1.0.1) Gecko/20021111 Chimera/0.6', 
'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 1.1.4322; Crazy Browser 2.0.1)', 
'Mozilla/4.0 (compatible; MSIE 8.0; AOL 9.5; AOLBuild 4337.29; Windows NT 6.0; Trident/4.0; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.5.21022; .NET CLR 3.5.30729; .NET CLR 3.0.30618)', 
'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-GB; rv:1.9.1.2) Gecko/20090729 Firefox/3.5.2 (.NET CLR 3.5.30729)', 
'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1b4pre) Gecko/20090409 Firefox/3.5b4pre', 
'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en-US; rv:1.0.1) Gecko/20021104 Chimera/0.6', 
'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Crazy Browser 3.0.0 Beta2)', 
'Mozilla/5.0 (Windows; U; Windows NT 6.0; de; rv:1.9.1.2) Gecko/20090729 Firefox/3.5.2 (.NET CLR 3.5.30729)', 
'Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.1; AOLBuild 4334.5000; Windows NT 5.1; Media Center PC 3.0; .NET CLR 1.0.3705; .NET CLR 1.1.4322; InfoPath.1)', 
'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1b2) Gecko/20060826 BonEcho/2.0b2', 
'Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6', 
'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.8.1.7) Gecko/20070918 BonEcho/2.0.0.7', 
'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/531.4 (KHTML, like Gecko) Chrome/3.0.194.0 Safari/531.4', 
'Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.89; Windows NT 6.0; SLCC1; .NET CLR 2.0.50727; .NET CLR 3.0.04506)', 
'Mozilla/5.0 (X11; U; Linux; de-DE) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.8.0', 
'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; Avant Browser; SLCC1; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30618; InfoPath.1)'
)

if __name__ == '__main__':
    pass
