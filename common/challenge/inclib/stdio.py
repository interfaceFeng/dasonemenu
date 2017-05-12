# -*- coding: utf-8 -*-
__all__ = ['Switch', 'Const', 'Define', 'Dict', 'List', 'LinkList']
__author__ = 'opencTM'
__version__ = '4.6.4'  # modify_count.class_count.bug_count
__license__ = 'MIF'


class Switch(object):
    """ -------------------------------------
        Switch for python switch case
        like c++ switch(*)
        made by opencTM@2015-05-08
        bugs can't continue or break from top
        -------------------------------------
        for case in Switch(raw_input(':')):
            if case('1'):
                print '==>1'
                break
            if case('2'):
                print '==>2'
                break
            if case('3'):
                print "==>3"
            if case('4'):
                print "==>4"
            if case('5'):
                print "==>5"
                break
            if case('10', '11', '12'):
                print '==>10, 11, 12'
                break
            if case():
                print 'Default'
                break
        --------------------------------- """
    class SwitchError(StopIteration):
        pass

    def __init__(self, value):
        self.fall = False
        self.value = value

    def __iter__(self):
        yield self.__case__
        raise self.SwitchError("Case Error!")

    def __case__(self, *args):
        if self.fall or not args:
            return True
        elif self.value in args:
            self.fall = True
            return True
        else:
            return False


class Const(object):
    """ -------------------------------------
        Const for python const veriable
        like c++ const *
        made by opencTM@2015-02-06
        add: ConstError by opencTM@2015-03-31

        modify by opencTM@2015-11-10:
            add: __iter__ inside method
            add: __call__ inside method
        modify by opencTM@2016-01-15:
            add: __setitem__ inside method
            add: __getitem__ inside method
        -------------------------------------
        c = Const(value='xxx')
        c.value: const 'xxx'
        c(): {'value': 'xxx'}
        c('value'): 'xxx'
        bugs: c.__dict__['value'] = 'xx' """
    class ConstError(TypeError):
        pass

    def __init__(self, **kwargs):
        object.__init__(self)
        for k in kwargs:
            self.__dict__[k] = kwargs.get(k)

    def __del__(self):
        for k in self.__dict__.keys():
            if hasattr(self, k):
                self.__delattr__(k)

    def __call__(self, key=None):
        return self.__dict__.get(key) if key else self.__dict__

    def __iter__(self):
        return iter(self.__dict__.keys())

    def __len__(self):
        return len(self.__dict__.keys())

    def __str__(self):
        return str(self.__dict__)

    def __setattr__(self, k, v):
        if k not in self.__dict__:
            self.__dict__[k] = v
            return
        raise self.ConstError("Can't rebind const: (%s)" % str(k))

    def __getitem__(self, k):
        return self.__call__(key=k)

    def __setitem__(self, key, val):
        return self.__setattr__(key, val)


class Define(object):
    """ --------------------------------------------
        Define for python define veriable
        like c++ define x x
        make by opencTM@2015-04-01
        --------------------------------------------
        c = Define('xxx')
        c.value: read-only 'xxx'
        c.value: c._Define__VALUE = 'x' escape
        bugs: c.__dict__['_Define__VALUE'] = 'x' """
    class DefineError(ValueError):
        pass

    def __init__(self, value):
        self.__VALUE = value

    def __int__(self):
        return int(self.__VALUE)

    def __str__(self):
        return str(self.__VALUE)

    def __len__(self):
        return len(self.__VALUE)

    def __setattr__(self, k, v):
        if not hasattr(self, k) and k == '_Define__VALUE':
            self.__dict__[k] = v
            return
        raise self.DefineError("Can't define %s" % str(k))

    def __delattr__(self, k):
        raise self.DefineError("Can't undef %s" % str(k))

    @property
    def value(self):
        return self.__VALUE

    @value.getter
    def value(self):
        return self.__VALUE

    @value.setter
    def value(self, value):
        raise self.DefineError("Can't rebind value: (%s)" % str(value))


class Dict(object):
    @staticmethod
    def dsort(dicts, comp=None, key=None, reverse=False):
        """ Breadth traversal dict
            sorting dictionary
            comp: locale.strcoll - chinese sort
            key: lambda c: dicts.get(c) - value sort """
        # locale.setlocale(locale.LC_COLLATE, 'zh_CN.UTF8')
        return sorted(dicts, cmp=comp, key=key, reverse=reverse)

    @staticmethod
    def dstrip(dicts, strips=(None, )):
        """ strip dicts if val is in strips """
        sp = [k for k in dicts if dicts[k] in strips]
        for k in sp:
            if k in dicts:
                dicts.pop(k)
        return

    @staticmethod
    def bool_to_int(dicts, keys=()):
        """ convert dicts bool to int """
        if not keys:
            for k in dicts:
                if (isinstance(k, int) or (isinstance(k, basestring) and k.isdigit())) and int(dicts[k]) in (0, 1):
                    dicts[k] = int(dicts[k])
        else:
            for k in dicts:
                if k in keys:
                    dicts[k] = 1 if int(dicts[k]) else 0
        return

    @classmethod
    def baseencode(cls, dicts, enc='utf-8'):
        """ Depth first traversal and postorder traversal key value
            From unicode encoding dicts to enc. """
        if isinstance(dicts, dict):
            for k in dicts.keys():
                if isinstance(dicts[k], dict):
                    # dict callback
                    cls.baseencode(dicts[k], enc)
                elif isinstance(dicts[k], list):
                    # list callback
                    List.baseencode(dicts[k], enc)
                elif isinstance(dicts[k], unicode):
                    # value is unicode
                    dicts[k] = dicts[k].encode(enc)
                if isinstance(k, unicode):
                    # key is unicode
                    bnode = k.encode(enc)
                    lnode = dicts.get(k)
                    dicts.pop(k)
                    dicts[bnode] = lnode
        return

    @classmethod
    def deepencode(cls, dicts, enc='utf-8'):
        """ Depth first traversal and postorder traversal key value
            From basestring decoding dicts and then encoding to enc. """
        if isinstance(dicts, dict):
            for k in dicts.keys():
                if isinstance(dicts[k], dict):
                    # dict callback
                    cls.deepencode(dicts[k], enc)
                elif isinstance(dicts[k], list):
                    # list callback
                    List.deepencode(dicts[k], enc)
                elif isinstance(dicts[k], str):
                    # value is str
                    dicts[k] = dicts[k].decode('raw_unicode_escape').encode(enc)
                elif isinstance(dicts[k], unicode):
                    # value is unicode
                    dicts[k] = dicts[k].encode(enc)
                if isinstance(k, str):
                    # key is str
                    bnode = k.decode('raw_unicode_escape').encode(enc)
                    lnode = dicts.get(k)
                    dicts.pop(k)
                    dicts[bnode] = lnode
                elif isinstance(k, unicode):
                    # key is unicode
                    bnode = k.encode(enc)
                    lnode = dicts.get(k)
                    dicts.pop(k)
                    dicts[bnode] = lnode
        return

    @classmethod
    def dwalk(cls, dicts, visitor, path=(), node=None):
        """ Depth first traversal and walking good dicts """
        for k in dicts:
            if k == node:
                visitor(path, dicts[k])
            if not isinstance(dicts[k], dict):
                pass
            else:
                # dict callback
                cls.dwalk(dicts[k], visitor, path + (k,), node)
        return

    @classmethod
    def lwalk(cls, dicts, visitor, path='', knode=None, separator='/', backout=False):
        """ Depth first traversal and preorder traversal dicts
            find kye-node, return leaf-node """
        for k, v in dicts.items():
            if k == knode:
                visitor(path, k, v)
                if backout:
                    return v
            if not isinstance(v, dict):
                pass
            else:
                # dict callback
                d = cls.lwalk(v, visitor, ''.join([path, separator, k]), knode, separator, backout)
                if d is not None and backout:
                    return d
        return

    @classmethod
    def pwalk(cls, dicts, visitor, path='', knode=None, separator='/', backout=False):
        """ Depth first traversal and preorder traversal dicts
            find key-node, return parent-node """
        for k, v in dicts.items():
            if v == knode:
                visitor(path, k, v)
                if backout:
                    return k
            if not isinstance(v, dict):
                pass
            else:
                # dict callback
                d = cls.pwalk(v, visitor, ''.join([path, separator, k]), knode, separator, backout)
                if d is not None and backout:
                    return d
        return

    @classmethod
    def lfind(cls, dicts, key):
        """ Breadth traversal and preorder traversal dicts
            find key's leaf-node """
        for k, v in dicts.items():
            if k == key:
                return v
            elif not isinstance(dicts[k], dict):
                pass
            else:
                # dict callback
                d = cls.lfind(dicts[k], key)
                if d is not None:
                    return d
        return

    @classmethod
    def kfind(cls, dicts, value):
        """ Breadth traversal and preorder traversal dicts
            find value's key """
        for k, v in dicts.items():
            if isinstance(v, (dict, list, tuple)) and value in v:
                return k
            elif isinstance(v, basestring) and value == v:
                return k
            elif isinstance(v, (bool, int, float, set, frozenset)) and value == v:
                pass
            elif not isinstance(v, dict):
                pass
            else:
                # dict callback
                d = cls.kfind(v, value)
                if d is not None:
                    return d
        return

    @staticmethod
    def lsearch(bnode, key):
        """ find branch-node's leaf-node """
        for k, v in bnode.items():
            if k == key:
                return v
        return

    @staticmethod
    def ksearch(bnode, value):
        """ find leaf-node's key """
        for k, v in bnode.items():
            if isinstance(v, (dict, list, tuple)) and value in v:
                return k
            elif isinstance(v, basestring) and value == v:
                return k
            elif isinstance(v, (bool, int, float, set, frozenset)) and value == v:
                pass
            else:
                pass
        return


class List(object):
    @staticmethod
    def lsort(lists, comp=None, key=None, reverse=False):
        """ Breadth traversal list
            sorting lists
            comp: locale.strcoll - chinese sort
            key: lambda c: lists.get(c) - value sort
            ip sort:
                comp = lambda x, y: cmp(''.join([i.rjust(3, '0') for i in x.split('.')]),
                                        ''.join([i.rjust(3, '0') for i in y.split('.')])) """
        # locale.setlocale(locale.LC_COLLATE, 'zh_CN.UTF8')
        return sorted(lists, cmp=comp, key=key, reverse=reverse)

    @staticmethod
    def lstrip(lists, strips=(None, )):
        """ strip lists if val is in strips """
        sp = [k for k in lists if k in strips]
        for k in sp:
            if k in lists:
                lists.pop(k)
        return

    @staticmethod
    def bool_to_int(lists, keys=()):
        """ convert lists bool to int """
        if not keys:
            for i in xrange(len(lists)):
                if (isinstance(lists[i], int) or (isinstance(lists[i], basestring) and lists[i].isdigit())) and int(lists[i]) in (0, 1):
                    lists[i] = int(lists[i])
        else:
            for i in xrange(len(lists)):
                if lists[i] in keys:
                    lists[i] = 1 if int(lists[i]) else 0
        return

    @classmethod
    def baseencode(cls, lists, enc='utf-8'):
        """ Depth first traversal and postorder traversal list value
            From unicode encoding lists to enc. """
        if isinstance(lists, list):
            for i in xrange(len(lists)):
                if isinstance(lists[i], list):
                    # list callback
                    cls.baseencode(lists[i], enc)
                elif isinstance(lists[i], dict):
                    # dict callback
                    Dict.baseencode(lists[i], enc)
                elif isinstance(lists[i], unicode):
                    # value is unicode
                    lists[i] = lists[i].encode(enc)
        return

    @classmethod
    def deepencode(cls, lists, enc='utf-8'):
        """ Depth first traversal and postorder traversal list value
            From basestring decoding lists and then encoding to enc. """
        if isinstance(lists, list):
            for i in xrange(len(lists)):
                if isinstance(lists[i], list):
                    # list callback
                    cls.deepencode(lists[i], enc)
                elif isinstance(lists[i], dict):
                    # dict callback
                    Dict.deepencode(lists[i], enc)
                elif isinstance(lists[i], str):
                    # value is str
                    lists[i] = lists[i].decode('raw_unicode_escape').encode(enc)
                elif isinstance(lists[i], unicode):
                    # value is unicode
                    lists[i] = lists[i].encode(enc)
        return

    @staticmethod
    def lunique(oldlist):
        """ Breadth traversal list
            unique lists """
        newlist = []
        for x in oldlist:
            if x not in newlist:
                newlist.append(x)
        return newlist

    @staticmethod
    def lseparator(strings, sep=' ', posix=True):
        """ string will be splist by sep """
        from shlex import shlex
        strval = shlex(strings, posix=posix)
        # strval.quotes = '"'
        strval.whitespace = sep
        strval.whitespace_split = True
        strlst = list(strval)
        del strval
        return strlst

    @staticmethod
    def lmatrix_inverse(matrix):
        """ 求矩阵的逆 """
        # 分配矩阵空间
        np = [[None for i in xrange(len(matrix))] for i in xrange(len(matrix[0]))]
        # 矩阵逆运算
        for i in xrange(len(matrix)):
            for j in xrange(len(matrix[i])):
                np[j][i] = matrix[i][j]
        return np

    @staticmethod
    def lmatrix_line_maxcell(matrix):
        """ 求矩阵行的最大值 """
        return [max(line, key=lambda c: c) for line in matrix]

    @staticmethod
    def lmatrix_line_maxsize(matrix):
        """ 求矩阵行的最大长度 """
        maxcell = [max(line, key=lambda c: len(str(c))) for line in matrix]
        return [len(str(cell)) for cell in maxcell]

    @classmethod
    def ltree(cls, dicts, lists, prefix, level):
        """ Breadth traversal and preorder traversal dicts
            create tree list buffer """
        count = len(dicts)
        for k, v in dicts.items():
            count -= 1
            if v:
                lists.append(''.join(["{0}".format(prefix), " +- ", "{0}".format(k)]))
                if count > 0:
                    # callback
                    cls.ltree(v, lists, ''.join([prefix, " |  "]), level + 1)
                else:
                    # callback
                    cls.ltree(v, lists, ''.join([prefix, "    "]), level + 1)
            else:
                lists.append(''.join(["{0}".format(prefix), " -- ", "{0}".format(k)]))
        return


class LinkList(object):
    """ LinkList for python structures
        like c++ struct *
        made by opencTM@2014-08-14

        modify by opencTM@2014-12-15:
            add1: len(linklist)
            add2: for i in linklist
            delete1: linklist.insert
            delete2: linklist.remove

        modify by opencTM@2014-12-25:
            add: linklist.sort

        modify by opencTM@2015-01-05:
            delete: linklist.delete
            add: linklist.remove(*keys)

        modify by opencTM@2015-04-29:
            bugs:
                object dumps to string

        modify by opencTM@2015-04-30:
            dicts with copy to cite

        modify by opencTM@2015-10-29:
            item with get, set, delete """

    def __init__(self, **kwargs):
        object.__init__(self)
        for key in kwargs:
            if not hasattr(self, key):
                self.__setattr__(key, kwargs.get(key))

    def __del__(self):
        """ del linklist """
        self.__delattrlist__(self.__getattrlist__())

    def __getitem__(self, key):
        """ get linklist item """
        return self.__dict__[key]

    def __setitem__(self, key, val):
        """ set linklist item """
        self.__setattr__(key, val)
        return

    def __delitem__(self, key):
        """ delete linklist item """
        del self.__dict__[key]
        return

    def __len__(self):
        """ len(linklist) """
        return len(self.__dict__.keys())

    def __str__(self):
        """ for print linklist """
        return self.dumps(ensure_ascii=False, encoding='utf-8')

    def __iter__(self):
        """ for i in linklist """
        return iter(self.__dict__.keys())

    def __getattrlist__(self):
        """ inside function """
        return self.__dict__.keys()

    def __delattrlist__(self, attrlist):
        """ inside function """
        for key in attrlist:
            if hasattr(self, key):
                self.__delattr__(key)
        return

    def __withtuple__(self, t):
        """ callback LinkList to get tuple """
        n = [None] * len(t)
        for i in xrange(len(t)):
            if isinstance(t[i], tuple):
                # tuple callback
                n[i] = self.__withtuple__(t[i])
            elif isinstance(t[i], list):
                # list callback
                n[i] = self.__withlist__(t[i])
            elif isinstance(t[i], dict):
                # dict callback
                n[i] = self.__withdict__(t[i])
            elif isinstance(t[i], LinkList):
                # linklist callback
                n[i] = t[i].__withlinklist__()
            elif isinstance(t[i], (type(None), bool, int, float, basestring, set)):
                n[i] = t[i]
            else:
                n[i] = str(t[i])
        return n

    def __withlist__(self, l):
        """ callback LinkList to get list """
        n = [None] * len(l)
        for i in xrange(len(l)):
            if isinstance(l[i], list):
                # list callback
                n[i] = self.__withlist__(l[i])
            elif isinstance(l[i], tuple):
                # tuple callback
                n[i] = self.__withtuple__(l[i])
            elif isinstance(l[i], dict):
                # dict callback
                n[i] = self.__withdict__(l[i])
            elif isinstance(l[i], LinkList):
                # linklist callback
                n[i] = l[i].__withlinklist__()
            elif isinstance(l[i], (type(None), bool, int, float, basestring, set)):
                n[i] = l[i]
            else:
                n[i] = str(l[i])
        return n

    def __withdict__(self, d):
        """ callback LinkList to get dict """
        n = {}
        for k in d:
            if isinstance(d.get(k), dict):
                # dict callback
                n[k] = self.__withdict__(d.get(k))
            elif isinstance(d.get(k), list):
                # list callback
                n[k] = self.__withlist__(d.get(k))
            elif isinstance(d.get(k), tuple):
                # tuple callback
                n[k] = self.__withtuple__(d.get(k))
            elif isinstance(d.get(k), LinkList):
                # linklist callback
                n[k] = d.get(k).__withlinklist__()
            elif isinstance(d.get(k), (type(None), bool, int, float, basestring, set)):
                n[k] = d.get(k)
            else:
                n[k] = str(d.get(k))
        return n

    def __withlinklist__(self):
        """ callback LinkList to get LinkList
            convert to dict """
        n = {}
        d = self.__dict__
        for k in d:
            if isinstance(d.get(k), LinkList):
                # linklist callback
                n[k] = d.get(k).__withlinklist__()
            elif isinstance(d.get(k), dict):
                # dict callback
                n[k] = self.__withdict__(d.get(k))
            elif isinstance(d.get(k), list):
                # list callback
                n[k] = self.__withlist__(d.get(k))
            elif isinstance(d.get(k), tuple):
                # tuple callback
                n[k] = self.__withtuple__(d.get(k))
            elif isinstance(d.get(k), (type(None), bool, int, float, basestring, set)):
                n[k] = d.get(k)
            else:
                n[k] = str(d.get(k))
        return n

    def sort(self, comp=None, key=None, reverse=False):
        """ Breadth traversal linklist
            sorting linklists by key
            comp: locale.strcoll - chinese sort
            key: lambda c: self.get(c) - value sort """
        # locale.setlocale(locale.LC_COLLATE, 'zh_CN.UTF8')
        return sorted(self, cmp=comp, key=key, reverse=reverse)

    def haskey(self, key):
        """ check key """
        if key in self.__getattrlist__():
            return True
        return False

    def keys(self):
        """ liknlist keys """
        return self.__getattrlist__()

    def values(self):
        """ linklist values """
        return [self.__getattribute__(key) for key in self.__getattrlist__() if hasattr(self, key)]

    def set(self, key, val):
        """ set key = value """
        self.__setattr__(key, val)
        return

    def get(self, key):
        """ get key's value """
        if hasattr(self, key):
            return self.__getattribute__(key)
        return

    def add(self, **kwargs):
        """ add keys = values """
        for key in kwargs:
            if not hasattr(self, key):
                self.__setattr__(key, kwargs.get(key))
        return

    def remove(self, *args):
        """ remove args """
        for key in args:
            if hasattr(self, key):
                self.__delattr__(key)
        return

    def clear(self):
        """ remove all method """
        return self.__delattrlist__(self.__getattrlist__())

    def dicts(self):
        """ copy LinkList to dict object """
        from copy import copy
        return copy(self.__withlinklist__())

    def dumps(self, skipkeys=False, ensure_ascii=True, check_circular=True,
              allow_nan=True, cls=None, indent=None, separators=None,
              encoding='utf-8', default=None, **kw):
        """ convert LinkList to json object """
        import json
        return json.dumps(self.__withlinklist__(),
                          skipkeys=skipkeys,
                          ensure_ascii=ensure_ascii,
                          check_circular=check_circular,
                          allow_nan=allow_nan, cls=cls,
                          indent=indent, separators=separators,
                          encoding=encoding, default=default, **kw)

    @classmethod
    def loads(cls, dic):
        """ convert dict object to LinkList
            other object will append to LinkList.objs """
        l = LinkList()
        if isinstance(dic, dict):
            for k in dic:
                if isinstance(dic.get(k), dict):
                    l.__setattr__(k, cls.loads(dic.get(k)))
                else:
                    l.__setattr__(k, dic.get(k))
        else:
            l.add(objs=dic)
        return l


if __name__ == '__main__':
    try:
        if 0:
            for case in Switch(raw_input('Select:')):
                if case('1'):
                    print "one"
                    break
                if case('2'):
                    print "tow"
                    break
                if case('10'):
                    print "ten"
                    break
                if case('100'):
                    print "one hundred"
                if case('1000'):
                    print "one thousand"
                if case('10000'):
                    print "ten thousand"
                    break
                if case('100000', '200000', '300000'):
                    print "one hundred thousand"
                if case():
                    print "how many?"
                    # break
        if 0:
            print '==>LinkList loads'
            dics = {'aa': [{'aaa': (['b1', 'b2', 'b3'], ['c1', 'c2', 'c3']),
                            'bbb': ['d1', 'd2'], 'ccc': 'ccc'},
                           {'ddd': 'ddd'},
                           ['e1', 'e2', 'e3']],
                    'bb': {'bbb': 'bbb'}}
            linklist = LinkList.loads(dics)
            print 'original dics: %s' % dics
            print 'linklist.loads: %s' % linklist.keys()
            print 'linklist.aa: %s' % linklist.aa
            print 'linklist.bb: %s' % linklist.bb
            print 'linklist.bb.bbb: %s' % linklist.bb.bbb
            print 'linklist.dicts: %s' % linklist.dicts()
            del linklist.aa
            del linklist.bb
            linklist.clear()
            del linklist
            print '\n'
        if 0:
            print '==>LinkList dumps:'
            linklist = LinkList(i=LinkList(ii='ii', iii=LinkList(iiii=[LinkList()])),
                                j=LinkList(jj={'jjj': LinkList(jjjj=[])}),
                                k={'kk': {'kkk': LinkList(kkkk={'kkkkk': 'kkkkk'})}},
                                l={'ll': LinkList(lll='lll')},
                                t=({'tt': LinkList(ttt={'tttt': (LinkList(ttttt='ttttt'), {'tttttt': 'tttttt'}, ['tttttt', 'ttttttt'])})},
                                   LinkList(ttttttt=())))
            print 'original linklist: %s' % linklist.keys()
            print 'linklist.i: %s' % linklist.i
            print 'linklist.j: %s' % linklist.j
            print 'linklist.k: %s' % linklist.k
            print 'linklist.t: %s' % str(linklist.t)
            print 'linklist.l: %s' % linklist.l
            print 'linklist.dicts: %s' % linklist.dicts()
            d = linklist.dumps()
            print 'linklist.dumps: %s' % d
            print 'linklist.loads(linklist.dumps): %s' % LinkList.loads(d).keys()
            print 'linklist.loads(linklist.dumps).objs: %s' % LinkList.loads(d).objs
            print 'linklist.loads(linklist.dumps).dicts: %s' % LinkList.loads(d).dicts()
            del d
            linklist.clear()
            del linklist
            print '\n'
        if 0:
            print '==>LinkList used:'
            linklist = LinkList(p=None, type=None, slot=LinkList())
            print zip(linklist.keys(), linklist.values())
            linklist.slot.script = 'basestring'
            print linklist.slot.script
            print linklist.get('slot').get('script')
            print linklist.haskey('slot')
            del linklist.slot
            print linklist.slot.dicts()
            linklist.clear()
            del linklist
            print '\n'
    except BaseException, e:
        print "Main error: %s" % str(e)
