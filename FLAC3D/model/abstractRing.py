# -*- coding: utf-8 -*-
from abstractGenerator import AbstractGenerator
from abstractEntity import AbstractEntity
from ..customDecorators import *


__all__ = ['AbstractRing', 'AbstractRing_Instance']


class AbstractRing(AbstractGenerator):
    def __init__(self, y_Bound_Global, propertyDict, eid, util, instanceClass):
        super(AbstractRing, self).__init__(instanceClass, util.modelUtil)
        self.eid = eid
        self.__util = util
        self.__id = (eid, util.n_Ring + 1)
        self.__groupList = []
        self.__propertyDict = propertyDict
        self.set_y_Bound_Global(y_Bound_Global)

    @property
    def id_Tuple(self):
        """以元组形式返回自定义ID编码"""
        return self.__id

    tid = id_Tuple

    @property
    def id_String(self):
        """以字符串形式返回自定义ID编码"""
        return '{structuralElementID:0>3}{sequenceNumber:0>2}'.format(
            structuralElementID=self.__id[0],
            sequenceNumber=self.__id[1]
        )

    sid = id_String

    @property
    def id(self):
        """以浮点数形式返回自定义ID编码"""
        return int(self.id_String)

    @property
    def sequenceNumber(self):
        return self.__id[1]

    @property
    def util(self):
        return self.__util

    @property
    def modelUtil(self):
        return self.__util.modelUtil

    @property
    def n_Group(self):
        return len(self.__groupList)

    @property
    def groups(self):
        return tuple(self.__groupList)

    def addGroup(self, group):
        self.__groupList.append(group)

    @property
    def propertyDict(self):
        return self.__propertyDict

    @y_Bound_Detect('y_Bound_Global')
    def set_y_Bound_Global(self, y_Bound_Global):
        self.y_Bound_Global = y_Bound_Global

    def calculateNodeCoord(self):
        pass


class AbstractRing_Instance(AbstractEntity):
    def __init__(self, y_Coord, parent, generator, manager):
        super(AbstractRing_Instance, self).__init__(parent, generator, manager)
        self.__id = (generator.tid[0], generator.tid[1], generator.n_Instance + 1)
        self.y_Coord = y_Coord
        self.__nodeList = []
        self.__elementList = []

    @property
    def id_Tuple(self):
        """以元组形式返回自定义ID编码"""
        return self.__id

    tid = id_Tuple

    @property
    def id_String(self):
        """以字符串形式返回自定义ID编码"""
        return '{structuralElementID:0>3}{sequenceNumber:0>2}.{instanceNumber:0>3}'.format(
            structuralElementID=self.__id[0],
            sequenceNumber=self.__id[1],
            instanceNumber=self.__id[2]
        )

    sid = id_String

    @property
    def id(self):
        """以浮点数形式返回自定义ID编码"""
        return round(float(self.id_String), 3)

    @property
    def sequenceNumber(self):
        return self.__id[1]

    @property
    def instanceNumber(self):
        return self.__id[2]

    ringNumber = instanceNumber

    @property
    def nodes(self):
        return tuple(self.__nodeList)

    @property
    def elements(self):
        return tuple(self.__elementList)

    def addNode(self, node):
        self.__nodeList.append(node)

    def addElement(self, element):
        self.__elementList.append(element)