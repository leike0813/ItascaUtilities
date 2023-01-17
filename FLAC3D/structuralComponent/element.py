# -*- coding: utf-8 -*-
import itasca as it
from abstractComponent import AbstractComponent

__all__ = ['Element']


class Element(AbstractComponent):
    def __init__(self, structElem_id, type_id, ringNumber, subElem_id, seqNumber, _cid, nodes, parent, manager):
        super(Element, self).__init__(structElem_id, type_id, ringNumber, subElem_id, seqNumber, _cid, parent, manager)
        self._nodes = nodes

    @property
    def pointer(self):
        """返回Itasca模型中的指针"""
        return it.structure.find(self._cid)

    def nodes(self):
        """Itasca自带nodes()接口的类比，返回由manager管理的单元相关节点的孪生实体对象构成的元组"""
        return self._nodes