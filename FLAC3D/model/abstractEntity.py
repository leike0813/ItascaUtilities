# -*- coding: utf-8 -*-

__all__ = ['AbstractEntity']


class AbstractEntity(object):
    def __init__(self, parent, manager):
        self.__parent = parent
        self.manager = manager

    @property
    def parent(self):
        return self.__parent