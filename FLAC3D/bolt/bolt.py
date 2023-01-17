# -*- coding: utf-8 -*-

from ..structuralComponent.element import Element
from ..model.abstractEntity import AbstractEntity


__all__ = ['BoltEntity', 'BoltRingEntity', 'BoltGroupEntity']


class BoltElement(Element):
    def __init__(self, structElem_id, ringNumber, subElem_id, seqNumber, _cid, nodes, parent, manager):
        super(BoltElement, self).__init__(structElem_id, 4, ringNumber, subElem_id, seqNumber, _cid, nodes, parent, manager)

    def __repr__(self):
        return 'Bolt element {_cid}'.format(_cid=self.pointer.component_id())

class BoltRingEntity(AbstractEntity):
    def __init__(self, y_Coord, boltRing, parent, manager):
        super(BoltRingEntity, self).__init__(parent, manager)
        self.y_Coord = y_Coord
        self.boltRing = boltRing
        self.boltGroupEntityList = []

    @property
    def ringNumber(self):
        return self.boltRing._instances.index(self) + 1

    def createBoltGroupEntity(self, boltGroup):
        _boltGroupEntity = BoltGroupEntity(boltGroup, self, self.manager)
        self.boltGroupEntityList.append(_boltGroupEntity)
        boltGroup._instances.append(_boltGroupEntity)
        return _boltGroupEntity


class BoltGroupEntity(AbstractEntity):
    def __init__(self, boltGroup, parent, manager):
        super(BoltGroupEntity, self).__init__(parent, manager)
        self.boltGroup = boltGroup
        self.boltEntityList = []

    def createBoltEntity(self):
        _boltEntity = BoltEntity(self, self.manager)
        self.boltEntityList.append(_boltEntity)
        return _boltEntity


class BoltEntity(AbstractEntity):
    def __init__(self, parent, manager):
        super(BoltEntity, self).__init__(parent, manager)
        self.elementList = []

    @property
    def subElem_id(self):
        return self.parent.boltEntityList.index(self) + 1

    def createBoltElement(self, seqNumber, _cid, nodes):
        _boltElement = BoltElement(
            self.parent.boltGroup._id,
            self.parent.parent.ringNumber,
            self.subElem_id,
            seqNumber,
            _cid,
            nodes,
            self,
            self.manager
        )
        self.elementList.append(_boltElement)
        return _boltElement