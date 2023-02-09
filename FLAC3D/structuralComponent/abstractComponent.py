# -*- coding: utf-8 -*-
from ..structuralComponent.abstractEntity import AbstractEntity

__all__ = ['AbstractComponent']


class AbstractComponent(AbstractEntity):
    def __init__(self, typeID, structuralElementID, ringNumber, subElementID, sequenceNumber, cid, parent, manager):
        super(AbstractComponent, self).__init__(parent=parent, manager=manager, generator=None)
        self.__id = (typeID, structuralElementID, ringNumber, subElementID, sequenceNumber)
        self.cid = cid

    @property
    def pointer(self):
        """返回Itasca模型中的指针，Node, Element和Link的具体实现方法不同"""
        return None

    pnt = pointer

    @property
    def id_String(self):
        """以字符串形式返回自定义ID编码"""
        return '{typeID:0>2}{structuralElementID:0>3}{ringNumber:0>3}{subElementID:0>2}.{sequenceNumber:0>3}'.format(
            typeID=self.__id[0],
            structuralElementID=self.__id[1],
            ringNumber=self.__id[2],
            subElementID=self.__id[3],
            sequenceNumber=self.__id[4]
        )

    sid = id_String

    @property
    def id(self):
        """以浮点数形式返回自定义ID编码"""
        return round(float(self.id_String),3)

    @property
    def typeID(self):
        return self.__id[0]

    @property
    def structuralElementID(self):
        return self.__id[1]

    eid = structuralElementID

    @property
    def ringNumber(self):
        return self.__id[2]

    @property
    def subElementID(self):
        return self.__id[3]

    @property
    def sequenceNumber(self):
        return self.__id[4]