#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#********************************
# pxhtmlbuilder:
#     HTML模版构造单元
#     输入模版和字典，生成HTML
# author:
#     zhangcheng
# version：
#   1.0（2008年03月18日）
#   1.1（2008年03月29日)
#     增加NIF条件
#   1.2（2008年05月16日）
#     修改了${var}中匹配空格的bug
#********************************

import os, re, time

version = '1.2'
name = 'Pylynx html builder'
__doc__ = '''
模版支持四种类型标签：
1.简单变量：${NAME}；其中NAME是变量名；
2.变量语句：<px:FLAG var="NAME" type="VAR">内容</px:FLAG>；其中FLAG是自定义标
  签，用于对应结束标签；NAME是变量名；VAR是关键字，表示是变量语句；内容用于预
  览；
3.条件语句：<px:FLAG var="NAME" type="IF">内容</px:FLAG>；其中IF是关键字，表示
  是条件语句；如果变量NAME为真，则内容部分会显示；
  条件语句：<px:FLAG var="NAME" type="NIF">内容</px:FLAG>；其中NIF是关键字，表示
  是条件语句；如果变量NAME不为真，则内容部分会显示；
4.循环语句：<px:FLAG var="NAME" type="LOOP">内容</px:FLAG>；其中IF是关键字，表
  示是条件语句；NAME变量对应了一个list或tuple，其各个值为一个字典，内容部分会被
  循环显示；
注：var和type是语句中的关键属性，属性值可以使用单引号或双引号包含，也可以不加引
号；变量语句中type属性可以省略；属性名称和属性值中不允许出现空格、换行、TAB、引
号；
'''

# 依据模版，生成HTML
# template: 模版
# vardict: 变量字典
# ignoreException: 是否忽略异常
def build(template, vardict, ignoreException = True):        
    restr = '''(?is).*?(?P<text><px(?P<f0>(?:\:(?P<name>\S+))?)(?:\s+var\s*=\s*(?P<f1>(?:"|')?)(?P<var>\S+?)(?P=f1)|\s+type\s*=\s*(?P<f2>(?:"|')?)(?P<type>\S+?)(?P=f2)|\s+\S+\s*=\s*(?P<f3>(?:"|')?)\S*?(?P=f3))+\s*(?:(?:/>)|(?:>(?P<intext>.*?)</px(?P=f0)\s*>))|\$\{(?P<svar>\S+?)\})'''
    recom = re.compile(restr)
    hlist = []
    lastpos = 0
    remat = recom.match(template)
    while remat:
        redict = remat.groupdict('')
        try:
            hlist.append(template[lastpos:remat.start('text')])
            lastpos = remat.end('text')
            text = redict['text']
            name = redict['name']
            var = redict['var']
            type = redict['type'].lower()
            intext = redict['intext']
            svar = redict['svar']
            if svar:
                hlist.append(str(vardict[svar]))
            elif type == 'var' or type == '':
                hlist.append(str(vardict[var]))
            elif type == 'if':
                if vardict[var]:
                    hlist.append(build(intext, vardict))
            elif type == 'nif':
                if not vardict[var]:
                    hlist.append(build(intext, vardict))
            elif type == 'loop':
                for rdict in vardict[var]:
                    hlist.append(build(intext, rdict))
        except Exception, args:
            if not ignoreException:
                raise Exception(str(args))
        remat = recom.match(template, remat.end())
    hlist.append(template[lastpos:])
    return ''.join(hlist)
        
def Test():
    template = '''svar = ${a}
loop = <px:1 var='b' type="loop"><px:2 var="c" type="if"><px:3 var="c" type="var">xxxx</px:3  > </px:2 ></px:1>
simple = <px var=d />yyy${a}&nbsp;${a}&nbsp;${a}&nbsp;
other = <px var=d xjdk=dkfd />
except = <px var=e />'''
    vardict = {}
    vardict['a'] = 'AAA'
    vardict['b'] = [{'c':0},{'c':1},{'c':2},{'c':'abcd'}]
    vardict['d'] = 'DDD'
    st = time.time()
    try:
        html = build(template, vardict, True)
    except Exception, args:
        html = 'Build exception: %s' % str(args)
    et = time.time()
    print 'Time used: %.3fms' % (et-st)
    print '------------------------------'
    print html
    print '------------------------------'

if __name__ == '__main__':
    Test()
    print '-END-'
    
    
