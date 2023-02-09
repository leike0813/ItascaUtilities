# -*- coding: utf-8 -*-
import itasca as it
from abstractComponent import AbstractComponent

__all__ = ['Element']


class Element(AbstractComponent):
    Beam = 30
    Cable = 40
    Pile = 50
    Shell = 60
    Liner = 70
    Geogrid = 80

    def __init__(self, typeID, structuralElementID, ringNumber, subElementID, sequenceNumber, cid, nodes, parent, manager):
        super(Element, self).__init__(typeID, structuralElementID, ringNumber, subElementID, sequenceNumber, cid, parent, manager)
        self._nodes = nodes

    @property
    def pointer(self):
        """返回Itasca模型中的指针"""
        return it.structure.find(self.cid)

    def nodes(self):
        """Itasca自带nodes()接口的类比，返回由manager管理的单元相关节点的孪生实体对象构成的元组"""
        return self._nodes

    def pos(self):
        """Itasca自带pos()接口的类比，返回单元坐标"""
        return self.pointer.pos()