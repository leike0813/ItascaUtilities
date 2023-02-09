# -*- coding: utf-8 -*-

__all__ = ['AbstractSubUtility']

class AbstractSubUtility(object):
    '''
    子util的抽象基类
    '''
    def __init__(self, model=None):
        self.__modelUtil = model
        self.__ringList = []

    @property
    def modelUtil(self):
        return self.__modelUtil

    @property
    def n_Ring(self):
        return len(self.__ringList)

    @property
    def rings(self):
        return tuple(self.__ringList)

    def addRing(self, ring):
        self.__ringList.append(ring)