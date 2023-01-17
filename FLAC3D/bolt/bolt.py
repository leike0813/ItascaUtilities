# -*- coding: utf-8 -*-

from ..structuralComponent.element import Element
from ..model.abstractEntity import AbstractEntity


__all__ = ['BoltElement', 'BoltEntity', 'BoltRingInstance', 'BoltGroupInstance']


class BoltElement(Element):
    def __init__(self, structElem_id, ringNumber, subElem_id, seqNumber, _cid, nodes, parent, manager):
        super(BoltElement, self).__init__(structElem_id, 4, ringNumber, subElem_id, seqNumber, _cid, nodes, parent, manager)

    def __repr__(self):
        return 'Bolt element {_cid} at {pos}'.format(
            _cid=self.pointer.component_id(),
            pos=self.pointer.pos()
        )

class BoltRingInstance(AbstractEntity):
    def __init__(self, y_Coord, boltRing, parent, manager):
        super(BoltRingInstance, self).__init__(parent, manager)
        self.y_Coord = y_Coord
        self.boltRing = boltRing
        self.boltGroupInstanceList = []

    def __repr__(self):
        return 'BoltRing instance at Y={y_Coord}'.format(y_Coord=self.y_Coord)

    @property
    def ringNumber(self):
        return self.boltRing._instances.index(self) + 1

    def createBoltGroupInstance(self, boltGroup):
        _boltGroupInstance = BoltGroupInstance(boltGroup, self, self.manager)
        self.boltGroupInstanceList.append(_boltGroupInstance)
        boltGroup._instances.append(_boltGroupInstance)
        return _boltGroupInstance


class BoltGroupInstance(AbstractEntity):
    def __init__(self, boltGroup, parent, manager):
        super(BoltGroupInstance, self).__init__(parent, manager)
        self.boltGroup = boltGroup
        self.boltEntityList = []

    def __repr__(self):
        return '{groupNumber}th bolt group instance at Y={y_Coord}'.format(
            groupNumber=self.groupNumber,
            y_Coord=self.parent.y_Coord
        )

    @property
    def groupNumber(self):
        return self.parnet.boltGroupInstanceList.index(self) + 1

    def createBoltEntity(self):
        _boltEntity = BoltEntity(self, self.manager)
        self.boltEntityList.append(_boltEntity)
        return _boltEntity


class BoltEntity(AbstractEntity):
    def __init__(self, parent, manager):
        super(BoltEntity, self).__init__(parent, manager)
        self.elementList = []

    def __repr__(self):
        return '{subElem_id}th bolt entity'.format(subElem_id=self.subElem_id)

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