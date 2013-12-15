# coding: UTF-8
from __future__ import absolute_import, division, print_function, unicode_literals
# @copyright ©2013, Rodrigo Cacilhας <batalema@cacilhas.info>

from importlib import import_module
from weakref import ref as weakref
from . import _lambda_relations

__all__ = ['Proxy']


class ProxyBase(object):

    def __init__(self, targetname):
        ProxyBase.__setattr__(self, '__targetname', targetname)
        ProxyBase.__setattr__(self, '__is_weakref', False)
        ProxyBase.__setattr__(self, '__set', False)


    def __import_target(self):
        name = ProxyBase.__getattribute__(self, '__targetname')
        if ':' in name:
            name, objname = name.split(':', 1)
        else:
            objname = None

        module = import_module(name)
        target = getattr(module, objname) if objname else module

        try:
            target = weakref(target)
        except TypeError:
            ProxyBase.__setattr__(self, '__is_weakref', False)
        else:
            ProxyBase.__setattr__(self, '__is_weakref', True)

        ProxyBase.__setattr__(self, '__target', target)
        ProxyBase.__setattr__(self, '__set', True)


    @property
    def _target(self):
        if not ProxyBase.__getattribute__(self, '__set'):
            ProxyBase.__import_target(self)
        target = ProxyBase.__getattribute__(self, '__target')
        if ProxyBase.__getattribute__(self, '__is_weakref'):
            target = target()
        return target


class ProxyMeta(type):

    props = (
        '__all__', '__doc__', '__file__', '__name__', '__package__',
    )

    meths = (
        '__delete__', '__delitem__', '__delslice__', '__div__',
        '__enter__', '__exit__', '__get__', '__index__', '__nonzero__',
        '__set__', '__setattr__', '__setitem__', '__setslice__',
        '__sizeof__', '__subclasshook__',

        '__abs__', '__add__', '__and__', '__bool__', '__call__',
        '__cmp__', '__coerce__', '__contains__', '__delattr__',
        '__dir__', '__divmod__', '__float__', '__floordiv__', '__eq__',
        '__ge__', '__getattr__', '__getitem__', '__getslice__',
        '__gt__', '__hash__', '__hex__', '__instancecheck__', '__int__',
        '__invert__', '__iter__', '__le__', '__len__', '__long__',
        '__lshift__', '__lt__', '__mod__', '__mul__', '__ne__',
        '__neg__', '__oct__', '__or__', '__pos__', '__pow__',
        '__radd__', '__rand__', '__rcmp__', '__rdiv__', '__repr__',
        '__reversed__', '__rfloordiv__', '__rlshift__', '__rmod__',
        '__rmul__', '__ror__', '__rpow__', '__rrshift__', '__rshift__',
        '__rsub__', '__rtruediv__', '__rxor__', '__str__', '__sub__',
        '__truediv__', '__unicode__', '__xor__',
    )


    def __new__(metaclass, name, bases, dct):
        for prop in metaclass.props:
            dct[prop] = metaclass.build_property(prop)

        for meth in metaclass.meths:
            dct[meth] = metaclass.build_method(meth)

        return type(name, bases, dct)


    @classmethod
    def build_property(metaclass, prop):
        return property(
            lambda self: getattr(super(Proxy, self)._target, prop)
        )


    @classmethod
    def build_method(metaclass, meth):
        if _lambda_relations.has(meth):
            return (
                lambda self, *args:
                    _lambda_relations.get(meth)(super(Proxy, self)._target, *args)
            )

        else:
            return (
                lambda self, *args:
                    getattr(super(Proxy, self)._target, meth)(*args)
            )



class Proxy(ProxyBase):

    __metaclass__ = ProxyMeta
    __dict__ = property(lambda self: vars(super(Proxy, self)._target))