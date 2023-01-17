# -*- coding: utf-8 -*-

__all__ = ['AbstractSubUtility']

class AbstractSubUtility(object):
    '''
    子util的抽象基类
    '''
    def __init__(self, model=None):
        self.modelUtil = model