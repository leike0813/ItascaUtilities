# -*- coding: utf-8 -*-
import itasca as it
from abstractComponent import AbstractComponent

__all__ = ['Node']


class Node(AbstractComponent):
    def __init__(self, structElem_id, ringNumber, subElem_id, seqNumber, _cid, parent, manager):
        super(Node, self).__init__(structElem_id, 1, ringNumber, subElem_id, seqNumber, _cid, parent, manager)

    def __repr__(self):
        return 'Structural Node {_cid}'.format(_cid=self.pointer.component_id())

    @property
    def pointer(self):
        """返回Itasca模型中的指针"""
        return it.structure.node.find(self._cid)
