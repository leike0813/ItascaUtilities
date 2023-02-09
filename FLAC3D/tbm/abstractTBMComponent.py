# -*- coding: utf-8 -*-
from ..model.abstractSubUtility import AbstractSubUtility


__all__ = ['AbstractTBMComponent']


class AbstractTBMComponent(AbstractSubUtility):
    '''
    TBM组件的抽象基类
    '''
    def __init__(self, groupList, propertyDict, eid, util):
        super(AbstractTBMComponent, self).__init__(util.modelUtil)
        self.__util = util
        self.groupList = groupList
        self.eid = eid
        self.propertyDict = propertyDict

    @property
    def util(self):
        return self.__util