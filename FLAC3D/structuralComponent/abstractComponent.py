# -*- coding: utf-8 -*-
import itasca as it
from ..model.abstractEntity import AbstractEntity

__all__ = ['AbstractComponent']


class AbstractComponent(AbstractEntity):
    def __init__(self, structElem_id, type_id, ringNumber, subElem_id, seqNumber, _cid, parent, manager):
        super(AbstractComponent, self).__init__(parent, manager)
        self._id = (structElem_id, type_id, ringNumber, subElem_id, seqNumber)
        self._cid = _cid

    @property
    def pointer(self):
        """返回Itasca模型中的指针，Node, Element和Link的具体实现方法不同"""
        return None

    pnt = pointer

    @property
    def ID_String(self):
        """以字符串形式返回自定义ID编码"""
        return '{structElem_id:0>3}{type_id:0>1}{ringNumber:0>3}{subElem_id:0>2}{seqNumber:0>3}'.format(
            structElem_id=self._id[0],
            type_id=self._id[1],
            ringNumber=self._id[2],
            subElem_id=self._id[3],
            seqNumber=self._id[4]
        )

    @property
    def ID(self):
        """以长整数形式返回自定义ID编码"""
        return int(self.ID_String)

    @property
    def structuralElementID(self):
        return self._id[0]

    @property
    def typeID(self):
        return self._id[1]

    @property
    def ringNumber(self):
        return self._id[2]

    @property
    def subElementID(self):
        return self._id[3]

    @property
    def seqenceNumber(self):
        return self._id[4]