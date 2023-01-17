# -*- coding: utf-8 -*-

__all__ = ['AbstractTBMComponent']

class AbstractTBMComponent(object):
    '''
    TBM组件的抽象基类
    '''
    def __init__(self, groupList, propertyDict, _id, tbmUtil):
        self.tbmUtil = tbmUtil
        self.modelUtil = tbmUtil.modelUtil
        self.groupList = groupList
        self._id = _id
        self.propertyDict = propertyDict