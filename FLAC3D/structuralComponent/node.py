# -*- coding: utf-8 -*-
import itasca as it
from abstractComponent import AbstractComponent

__all__ = ['Node']


class Node(AbstractComponent):
    def __init__(self, structuralElementID, ringNumber, subElementID, sequenceNumber, cid, parent, manager):
        super(Node, self).__init__(10, structuralElementID, ringNumber, subElementID, sequenceNumber, cid, parent, manager)

    def __repr__(self):
        return 'Structural Node {cid} at {pos}'.format(
            cid=self.pointer.component_id(),
            pos=tuple(round(coord, 3) for coord in self.pointer.pos())
        )

    @property
    def pointer(self):
        """返回Itasca模型中的指针"""
        return it.structure.node.find(self.cid)

    def pos(self):
        """Itasca自带pos()接口的类比，返回节点坐标"""
        return self.pointer.pos()
