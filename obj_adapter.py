#!/usr/bin/python
#-*- coding: utf-8 -*-

#********************************
#    FileName: obj_adapter.py
#    Author  : ghostwwl
#    Email   : wule@jd.com
#    Date    : 2019-1-22
#    Note    : 2019.04.09 加入msgpack 格式
#********************************


__author__ = "ghostwwl"

import os
import pickle
try:
    import ujson as json
except ImportError:
    import json
import yaml
import msgpack


# -------------------------------------------------------------------------------------------
class AdapterInterface(object):
    def do_import(self, obj_file):
        raise NotImplementedError

    def do_export(self, obj, obj_file):
        raise NotImplementedError

    def do_import_bytestr(self, obj_content_str):
        raise NotImplementedError

    def do_export_bytestr(self, obj):
        raise NotImplementedError

# -------------------------------------------------------------------------------------------
class BaseAdapter(AdapterInterface):
    def file_check(self, f):
        if not os.path.exists(f):
            raise OSError('File {0} Not Exists'.format(f))

# -------------------------------------------------------------------------------------------
class ObjAdapter(BaseAdapter):
    def __init__(self):
        self.engine = pickle

    def do_import(self, obj_file):
        self.file_check(obj_file)
        with open(obj_file, 'rb') as objf:
            return self.engine.load(objf)

    def do_export(self, obj, obj_file):
        with open(obj_file, 'wb') as objf:
            return self.engine.dump(obj, objf)

    def do_import_bytestr(self, obj_content_str):
        return self.engine.loads(obj_content_str)

    def do_export_bytestr(self, obj):
        return self.engine.dumps(obj)

# -------------------------------------------------------------------------------------------
class JsonAdapter(ObjAdapter):
    def __init__(self):
        self.engine = json

    def do_import(self, obj_file):
        self.file_check(obj_file)
        with open(obj_file, 'r') as objf:
            return self.engine.load(objf)

    def do_export(self, obj, obj_file):
        with open(obj_file, 'w') as jsonf:
            return self.engine.dump(obj, jsonf, sort_keys=True, indent=4, ensure_ascii=False)

# -------------------------------------------------------------------------------------------
class YamlAdapter(JsonAdapter):
    def __init__(self):
        self.engine = yaml

    def do_export(self, obj, obj_file):
        with open(obj_file, 'w') as yamlf:
            return self.engine.dump(obj, yamlf, indent=4, allow_unicode=True)

    def do_import_bytestr(self, obj_content_str):
        return self.engine.load(obj_content_str)

    def do_export_bytestr(self, obj):
        return self.engine.dump(obj)

# -------------------------------------------------------------------------------------------
class MsgpackAdapter(ObjAdapter):
    def __init__(self):
        self.engine = msgpack

    def do_import(self, obj_file):
        self.file_check(obj_file)
        with open(obj_file, 'rb') as objf:
            return self.engine.load(objf, raw=False)

    def do_import_bytestr(self, obj_content_str):
        return self.engine.unpackb(obj_content_str, raw=False)

    def do_export_bytestr(self, obj):
        return self.engine.packb(obj)

# -------------------------------------------------------------------------------------------
def get_adapter(xtype=1):
    if xtype == 0:
        return ObjAdapter
    if xtype == 1:
        return JsonAdapter
    if xtype == 2:
        return YamlAdapter
    if xtype == 3:
        return MsgpackAdapter
    raise Exception('Unsuited object file format')

class ImportAdapter(object):
    def __init__(self, in_type=1):
        self.import_process = get_adapter(in_type)()

    def do_import(self, obj_file):
        return self.import_process.do_import(obj_file)

    def do_import_bytestr(self, obj_content_str):
        return self.import_process.do_import_bytestr(obj_content_str)

# -------------------------------------------------------------------------------------------
class ExportAdapter(object):
    def __init__(self, out_type=1):
        self.export_porcess = get_adapter(out_type)()

    def do_export(self, obj, obj_file):
        return self.export_porcess.do_export(obj, obj_file)

    def do_export_bytestr(self, obj):
        return self.export_porcess.do_export_bytestr(obj)

if __name__ == '__main__':
    pass
