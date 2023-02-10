# -*- coding: utf-8 -*-
from abstractGenerator import AbstractGenerator
from abstractEntity import AbstractEntity
import numpy as np


__all__ = ['AbstractGroup', 'AbstractGroup_Instance']


class AbstractGroup(AbstractGenerator):
    def __init__(self, n_Seg, eid, ring, instanceClass):
        super(AbstractGroup, self).__init__(instanceClass, ring.modelUtil)
        self.n_Seg = n_Seg
        self.eid = eid
        self.__ring = ring
        self.__id = (eid, ring.sequenceNumber, ring.n_Group + 1)
        self.__nodeCoord = None
        self.instantiate_Param_List.extend(['eid', 'n_Seg'])

    @property
    def id_Tuple(self):
        """以元组形式返回自定义ID编码"""
        return self.__id

    tid = id_Tuple

    @property
    def id_String(self):
        """以字符串形式返回自定义ID编码"""
        return '{structuralElementID:0>3}{ringSequenceNumber:0>2}{sequenceNumber:0>2}'.format(
            structuralElementID=self.__id[0],
            ringSequenceNumber=self.__id[1],
            sequenceNumber=self.__id[2]
        )

    sid = id_String

    @property
    def id(self):
        """以浮点数形式返回自定义ID编码"""
        return int(self.id_String)

    @property
    def sequenceNumber(self):
        return self.__id[2]

    @property
    def ring(self):
        return self.__ring

    @property
    def util(self):
        return self.__ring.util

    @property
    def modelUtil(self):
        return self.__ring.modelUtil

    @property
    def nodeCoord(self):
        return self.__nodeCoord

    def setNodeCoord(self, arr):
        self.__nodeCoord = arr
        if type(arr) is np.ndarray:
            self.__nodeCoord.flags.writeable = False
            self.ring.calculateNodeCoord()

    @property
    def previousGroup(self):
        return self.ring.groups[self.sequenceNumber - 2] if self.sequenceNumber > 1 else None


class AbstractGroup_Instance(AbstractEntity):
    def __init__(self, y_Coord, parent, generator, manager):
        super(AbstractGroup_Instance, self).__init__(parent, generator, manager)
        self.__id = (
            generator.tid[0],
            generator.tid[1],
            generator.tid[2],
            parent.instanceNumber,
            generator.n_Instance + 1
        )
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
        return '{structuralElementID:0>3}{ringSequenceNumber:0>2}{sequenceNumber:0>2}.{ringInstanceNumber:0>3}{instanceNumber:0>3}'.format(
            structuralElementID=self.__id[0],
            ringSequenceNumber=self.__id[1],
            sequenceNumber=self.__id[2],
            ringInstanceNumber=self.__id[3],
            instanceNumber=self.__id[4]
        )

    sid = id_String

    @property
    def id(self):
        """以浮点数形式返回自定义ID编码"""
        return round(float(self.id_String), 6)

    @property
    def sequenceNumber(self):
        return self.__id[2]

    @property
    def instanceNumber(self):
        return self.__id[4]

    @property
    def ringNumber(self):
        return self.__id[3]

    @property
    def nodes(self):
        return tuple(self.__nodeList)

    @property
    def elements(self):
        return tuple(self.__elementList)

    @property
    def previousGroup_Instance(self):
        return self.parent.children[self.sequenceNumber - 2] if self.sequenceNumber > 1 else None

    def addNode(self, node):
        self.__nodeList.append(node)

    def addElement(self, element):
        self.__elementList.append(element)