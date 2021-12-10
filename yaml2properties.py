#!/usr/bin/python
#-*- coding: utf-8 -*-

# ***************************************
#    FileName: yaml2properties.py
#    Author  : ghostwwl
#    Email   : ghostwwl@gmail.com
#    Date    : 2021
#    Note    : 把 yaml 对象编码为 properties kv
# ***************************************

__author__ = "ghostwwl"

import re
import typing
import datetime

# Yaml 数据类型

# 1. 标量: scalar
# 字符串
# 布尔值
# 整数
# 浮点数
# Null
# 时间
# 日期
# 2. 对象: 键值对的集合, 映射（mapping）/ 哈希（hashes） / 字典（dictionary）
# 3. 数组：一组按次序排列的值，又称为序列（sequence） / 列表（list）


class YamlType(object):
    TYPE_OPCODE = {
        dict: 1,
        list: 2,
        tuple: 2,
        str: 3,
        bool: 4,
        int: 5,
        float: 6,
        type(None): 7,
        datetime.datetime: 8,
        datetime.date: 9,
    }

    @classmethod
    def is_valid_yaml_type(cls, opcode: typing.Any) -> bool:
        return opcode in cls.TYPE_OPCODE

    @classmethod
    def get_val_yaml_type(cls, val: typing.Any) -> int:
        t_val = type(val)
        if t_val in cls.TYPE_OPCODE:
            return cls.TYPE_OPCODE[t_val]
        return -1


#-----------------------------------------------------------------------------------------
class Yaml2Properties(YamlType):
    @classmethod
    def encode_scalar_variable(cls, type_code: int, sval: typing.Any) -> str:
        """
        对 yaml 标量进行编码
        :param type_code:   标量类型编码
        :param sval:        标量值
        :return:
        """
        if type_code == 4:
            return 'true' if sval else 'false'
        if type_code in (5, 6):
            return sval
        elif type_code == 7:
            return 'Null'
        elif type_code == 8:
            return sval.strftime('%Y-%m-%d %H:%M:%S')
        elif type_code == 9:
            return sval.strftime('%Y-%m-%d')
        else:
            return f"{sval}"

    @classmethod
    def encode_array_variable(cls, sval: typing.Any, parent_key=None, result_obj=None) -> None:
        """
        编码 array 类型对象
        :param sval:
        :param parent_key:
        :param result_obj:
        :return:
        """
        if result_obj is None:
            result_obj = {}

        for inx in range(len(sval)):
            obj_key = f"[{inx}]"
            if parent_key is not None:
                obj_key = '{0}{1}'.format(parent_key, obj_key)

            v = sval[inx]
            v_type_code = cls.get_val_yaml_type(v)
            if 1 == v_type_code:
                cls.encode_object_variable(v, obj_key, result_obj)
            elif 2 == v_type_code:
                cls.encode_array_variable(v, obj_key, result_obj)
            else:
                result_obj[obj_key] = cls.encode_scalar_variable(v_type_code, v)

    @classmethod
    def encode_object_variable(cls, sval: typing.Any, parent_key=None, result_obj=None) -> None:
        """
        编码 object 类型对象
        :param sval:
        :param parent_key:
        :param result_obj:
        :return:
        """
        if result_obj is None:
            result_obj = {}

        for k, v in sval.items():
            if parent_key is None:
                obj_key = k
            else:
                obj_key = '{0}.{1}'.format(parent_key, k)

            v_type = type(v)
            v_type_code = cls.get_val_yaml_type(v)
            if 1 == v_type_code:
                cls.encode_object_variable(v, obj_key, result_obj)
            elif 2 == v_type_code:
                cls.encode_array_variable(v, obj_key, result_obj)
            else:
                result_obj[obj_key] = cls.encode_scalar_variable(cls.TYPE_OPCODE[v_type], v)

    TEMPLATE_PATTERN_MATCHER = re.compile(r'\$\{(?P<PATTERN_NAME>[^\}]*?)\}')
    def template_render(self, content: str, var_dict: typing.Dict[str, typing.Any] = None, xml_quote=False) -> str:
        """
        极简模板解析器，只支持 ${var} 这一种变量格式

        :param content:  模板文件内容
        :param var_dict:        变量字典
        :return:                模板解析生成后的新内容
        """
        hlist = []
        last_pos = 0
        last_match_start = 0
        for matched_pattern in self.TEMPLATE_PATTERN_MATCHER.finditer(content):
            hlist.append(content[last_pos:matched_pattern.start()])
            var_name = matched_pattern.groupdict().get("PATTERN_NAME")
            if var_name not in var_dict:
                # var_dict 里不存在的保持原样输出
                hlist.append("${%s}" % var_name)
            else:
                if xml_quote:
                    hlist.append(self.quote_xml(var_dict[var_name]))
                else:
                    hlist.append(var_dict[var_name])
            last_pos = matched_pattern.end()
            last_match_start = matched_pattern.start()

        if last_pos > last_match_start:
            hlist.append(content[last_pos:])

        # content 不是模板文件的情况
        if last_pos == last_match_start and last_pos == 0:
            return content

        return ''.join(hlist)

    def quote_xml(self, r: str) -> str:
        """
        处理xml中5个预定义实体引用
        :param xml:
        :return:
        """
        return r.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").\
            replace("'", "&apos;").replace('"', "&quot;")


    def encode(self, yaml_obj: typing.Any, key_info=None, result_obj=None) -> typing.Dict[str, str]:
        """
        对 yaml 解析后的对象进行编码
        yaml_obj --> properties kv

        :param yaml_obj:  yaml 解析后的 python 对象
        :return:
        """

        if result_obj is None:
            result_obj = {}

        # 1. 获取 yaml 对象 根节点类型 因为 '"a"' 这也可以认为是一个yaml 对象
        root_type_code = self.get_val_yaml_type(yaml_obj)

        if 1 == root_type_code:
            # a. 如果是 object 对象
            self.encode_object_variable(yaml_obj, key_info or None, result_obj)
        elif 2 == root_type_code:
            # b. 如果根节点是数组
            self.encode_array_variable(yaml_obj, key_info or None, result_obj)

        for k, v in result_obj.items():
            if not isinstance(v, str):
                continue

            result_obj[k] = self.template_render(v, result_obj)

        return result_obj


#-----------------------------------------------------------------------------------------


if __name__ == "__main__":
    y = '''
TT: ToolTT.
Movies:
    - Movie: {title: E.T., year: 2020}
    - Movie: {title: Jaws, year: 2021}
    
cool_list:
  - 10
  - 15
  - 12

hard_list:
  - {key: value}
  - [1,2,3]
  - test:
      - 1
      - 2
      - 3

twice_list:
  -
    - {c: d}
    - {e: f}
    - {a: b}
    '''
    import yaml
    yobj = yaml.safe_load(y)
    print(yobj)

    T = Yaml2Properties()
    r = T.encode(yobj)
    import pprint
    pprint.pprint(r)
