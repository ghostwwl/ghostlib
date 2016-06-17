#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
#  xxxx.artxun.com  
#  pycgi for ngxin
#

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import time, os, sys
import md5
import base64
import re
import types
import urllib

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
__LIBPAHT__ = os.path.join(ROOT_PATH, 'lib')
if __LIBPAHT__ not in sys.path:
    sys.path.insert(1, __LIBPAHT__)

from pxoracle import ClassOracle
from pxmysql import ClassMySql
from phpserialize import serialize, unserialize


from tornado.options import define, options

define("port", default=8880, help="run on the given port", type=int)



ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
class PaimaiHandler(tornado.web.RequestHandler):
    def get(self):
        ready_do_py = self.request.arguments.get('py', [None,])[0]
        if ready_do_py is None: raise tornado.web.HTTPError(404)
        pyfile = '%s.py' % os.path.join(ROOT_PATH, 'paimai', ready_do_py)
        if not os.path.exists(pyfile): raise tornado.web.HTTPError(404)
        try:
            execfile(pyfile)
        except Exception,e:
            tornado.web.HTTPError(500, '破代码执行错误')

    def post(self):
        ready_do_py = self.request.arguments.get('py', [None,])[0]
        if ready_do_py is None: raise tornado.web.HTTPError(404)
        pyfile = '%s.py' % os.path.join(base_path,  'paimai', ready_do_py)
        if not os.path.exists(pyfile): raise tornado.web.HTTPError(404)
        try:
            execfile(pyfile)
        except Exception,e:
            tornado.web.HTTPError(500, '破代码执行错误')

    def do_rewrite(self, html):
        rewrite_reobj = re.compile("(?is).*?(?P<body>(?P<fprev>href\s*=\s*[\'\"]?)(?:http\://xxxxx\.artxun\.com)?(?:/zxp/new/|/py){1}[/]?(?P<fname>p|s|do)(?:\.php)?[\?]?(?P<fparam>[^\#\'\"\>]*?)(?P<fnext>[\#\'\"\>]))")
        startpos = 0
        outlist = []
        remat = rewrite_reobj.match(html)
        while remat:
            redict = remat.groupdict()
            outlist.append(html[startpos:remat.end() - len(remat.groups()[0])])
            body = redict.get('body', '')
            fprev = redict.get('fprev', '')
            fname = redict.get('fname', '')
            fparam = redict.get('fparam', '')
            fnext = redict.get('fnext', '')
            fparam = fparam.replace('&amp;', '&')
            params = dict(map(lambda x: tuple(x.split('=', 1)), filter(lambda x:len(x), fparam.split('&'))))
            url = '';
            if fname == 'do':
                if params.get('py', '') == 'd':
                    sid = params.get('id', '')
                    state = '-%s' % params.get('state', '') if params.get('state', None) else '-'
                    p = '-%s' % params.get('p', '') if params.get('p', None) else ''
                    url = "/finish/goods-%s%s%s.html" % (sid, state, p)
                elif params.get('py', '') == 's':
                    spname = params.get('s', '')
                    if spname and '%' not in spname:
                        spname = urllib.quote(spname)
                    state = '%s' % params.get('state', '')
                    p = '%s' % params.get('p', '1')
                    url = "/special-%s/index%s-%s.html" % (spname, state, p)
            if url: body = "%s%s%s" % (fprev, url, fnext)
            outlist.append(body)
            startpos = remat.end()
            remat = rewrite_reobj.match(html, startpos)

        outlist.append(html[startpos:])
        return ''.join(outlist)

    def rc4_authcode(self, instr, operation='DECODE', expiry=0):
        if operation == 'DECODE' and ' ' in instr:
            instr = instr.replace(' ', '+')
        key = '**************************'
        ckey_length = 4

        key = md5.new(key).hexdigest()
        keya = md5.new(key[:16]).hexdigest()
        keyb = md5.new(key[16:32]).hexdigest()
        keyc = instr[:ckey_length] if operation == 'DECODE' else md5.new(str(time.time()*1000)).hexdigest()[0-ckey_length:]

        cryptkey = '%s%s' % (keya, md5.new('%s%s' % (keya, keyc)).hexdigest())
        key_length = len(cryptkey)

        if operation == 'DECODE':
            instr = base64.b64decode(instr[ckey_length:] + '==')
        else:
            instr = '0000000000%s%s' % (md5.new('%s%s' % (instr, keyb)).hexdigest()[:16], instr)
        string_length = len(instr)

        result = ''
        box = {}
        rndkey = {}

        for i in xrange(256):
            box[i]=i
            rndkey[i] = ord(cryptkey[i % key_length])

        j = 0
        for i in xrange(256):
            j = (j + box[i] + rndkey[i]) % 256
            tmp = box[i]
            box[i] = box[j]
            box[j] = tmp


        a = j =0;

        for i in xrange(string_length):
            a = ( a + 1 ) % 256
            j = ( j + box[a] ) % 256
            tmp = box[a]
            box[a] = box[j]
            box[j] = tmp

            result += chr(ord(instr[i]) ^ (box[(box[a] + box[j]) % 256]))

        if operation == 'DECODE':
            if result[:10].isdigit():
                if int(result[:10]) == 0: return result[26:]
                if int(result[:10]) - time() > 0 and result[10:26] == md5.new(result[:26].keyb).hexdigest()[:16] : return result[26:]
                return ''
            else: return ''
        else:
            return keyc + base64.b64encode(result).replace('=', '')

    def conver_dict_unicode(self, indic):
        for k in indic:
            if type(indic[k]) is types.StringType:
                if indic[k].isdigit():
                    indic[k] = int(indic[k])
                else:
                    indic[k] = unicode(indic[k], 'utf-8', 'ignore')
            elif type(indic[k]) is types.DictionaryType:
                self.conver_dict_unicode(indic[k])
            elif type(indic[k]) in (types.ListType, types.TupleType):
                map(self.conver_dict_unicode, indic[k])

    def _make_page_obj(self, total, pn, maxpg, pagesize, pname, baseurl='', plen=10):
        pages = {}
        pagecount = maxpg
        if not baseurl:
            baseurl = "%s?%s" % (self.request.path, re.sub('[&\?]?p=\d{0,}', '', self.request.uri.split('?', 1)[1]))
        # firstpage
        if pagecount >= 1: pages['firstpage'] = baseurl
        # prevpage
        if pn > 1: pages['prevpage'] = baseurl if pn == 2 else "%s&%s=%d" % (baseurl, pname, pn - 1)
        # nextpage
        if pn < pagecount: pages['nextpage'] = "%s&%s=%d" % (baseurl, pname, pn + 1)
        # lastpage
        if pagecount >= 1: pages['lastpage'] = baseurl if pagecount == 1 else "%s&%s=%d" % (baseurl, pname, pagecount)
        # pagelist:[is_cur|page|pageurl]
        pages['pagelist'] = []
        s = pn - max(int(plen/2), plen - pagecount + pn -1)
        for i in xrange(s, pn+plen, 1):
            if i >= pn + plen: break
            if i <=0 or i > pagecount: continue
            if len(pages['pagelist']) >= plen: break
            item = {}
            item['is_cur'] = True if i == pn else False
            item['page'] = i
            item['pageurl'] = baseurl if i == 1 else "%s&%s=%d" % (baseurl, pname, i)
            pages['pagelist'].append(item)
        pages['total'] = total
        pages['pagecount'] = pagecount
        pages['curpage'] = pn
        pages['pagesize'] = pagesize
        pages['baseurl'] = baseurl
        return pages

    def parse_xml_iter(self, data, root_str):
        root_len = len(root_str) + 2
        root_lene = root_len + 1
        records = []
        lp = sn = 0
        while 1:
            ps = data.find("<%s>" % root_str, lp)
            if ps < 0: break
            data_s = ps + root_len
            pe = data.find("</%s>" % root_str, data_s)
            if ps < 0: break
            record = data[data_s:pe]
            item = {}
            flp = 0
            sn += 1
            while 1:
                fs = record.find('<', flp)
                if fs < 0: break
                fss = fs + 1
                fe = record.find('>', fss)
                if fe < 0: break
                fname = record[fss:fe]
                if not fname: break
                fbs = fs + 2 + fe - fss
                fb = record.find("</%s>" % fname, fbs)
                if fb < 0: break
                fds = fb - fbs
                fdata = record[fbs:fb]
                if fds >= 12 and fdata.find('<![CDATA[') >= 0  and fdata.find(']]>') >= 0:
                    fdata = fdata[9:-3]
                item[fname] = fdata
                flp = fb + 3 + fe - fss
            item['sn'] = sn
            if sn == 1: item['isfirst'] = 1
            records.append(item)
            lp = pe + root_lene
        return records

def main():
    tornado.options.parse_command_line()
    settings = {
        "static_path": os.path.join(os.path.dirname(__file__), "paimai", "templates") 
    }
    application = tornado.web.Application([
        (r"/py/do", PaimaiHandler),
        ], **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()



if __name__ == "__main__":
    main()
