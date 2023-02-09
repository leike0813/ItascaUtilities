# -*- coding: utf-8 -*-

__all__ = ['AbstractEntity']


#class AbstractEntity(object):
class AbstractEntity(object):
    def __init__(self, parent, generator, manager):
        self.__parent = parent
        self.__generator = generator
        self.__manager = manager
        self.__children = []

    @property
    def parent(self):
        return self.__parent

    @property
    def generator(self):
        return self.__generator

    @property
    def manager(self):
        return self.__manager

    @property
    def children(self):
        return tuple(self.__children)

    @property
    def n_Child(self):
        return len(self.__children)

    def addChild(self, child):
        self.__children.append(child)

    def update_Param(self, _dict):
        self.__dict__.update(_dict)


# class AbstractEntity(object):
#     def initialize(self):
#         self.__children = []
#
#     @property
#     def parent(self):
#         return self.__parent
#
#     @property
#     def generator(self):
#         return self.__class__
#
#     @property
#     def manager(self):
#         return self.__manager
#
#     @property
#     def children(self):
#         return tuple(self.__children)
#
#     @property
#     def n_Child(self):
#         return len(self.__children)
#
#     def addChild(self, child):
#         self.__children.append(child)
#
#     def update_Param(self, _dict):
#         self.__dict__.update(_dict)