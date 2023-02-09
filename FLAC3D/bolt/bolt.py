# -*- coding: utf-8 -*-

import itasca as it
from ..structuralComponent.node import Node
from ..structuralComponent.element import Element
from ..structuralComponent.abstractEntity import AbstractEntity


__all__ = ['BoltElement', 'BoltEntity']


class BoltElement(Element):
    def __init__(self, structuralElementID, ringNumber, subElementID, sequenceNumber, cid, nodes, parent, manager):
        super(BoltElement, self).__init__(Element.Cable, structuralElementID, ringNumber, subElementID, sequenceNumber, cid, nodes, parent, manager)

    def __repr__(self):
        return 'Bolt element {cid} at {pos}'.format(
            cid=self.pointer.component_id(),
            pos=tuple(round(coord, 3) for coord in self.pointer.pos())
        )


class BoltEntity(AbstractEntity):
    def __init__(self, begin_Coord, end_Coord, n_Seg, parent, manager):
        super(BoltEntity, self).__init__(parent=parent, manager=manager, generator=None)
        self.__id = (
            self.parent.tid[0],
            self.parent.tid[1],
            self.parent.tid[2],
            self.parent.n_Child + 1,
            self.parent.tid[3],
            self.parent.tid[4]
        )
        self.__begin_Coord = tuple(begin_Coord)
        self.__end_Coord = tuple(end_Coord)
        self.__n_Seg = n_Seg
        self.__nodeList = []
        self.__elementList = []

    def __repr__(self):
        return '{subElementID}th bolt entity at {beginPos}'.format(
            subElementID=self.subElementID,
            beginPos=self.begin_Coord
        )

    @property
    def id_Tuple(self):
        """以元组形式返回自定义ID编码"""
        return self.__id

    tid = id_Tuple

    @property
    def id_String(self):
        """以字符串形式返回自定义ID编码"""
        return '{structuralElementID:0>3}{ringSequenceNumber:0>2}{groupSequenceNumber:0>2}{subElementID:0>2}.{ringInstanceNumber:0>3}{groupInstanceNumber:0>3}'.format(
            structuralElementID=self.__id[0],
            ringSequenceNumber=self.__id[1],
            groupSequenceNumber=self.__id[2],
            subElementID=self.__id[3],
            ringInstanceNumber=self.__id[4],
            groupInstanceNumber=self.__id[5]
        )

    sid = id_String

    @property
    def id(self):
        """以浮点数形式返回自定义ID编码"""
        return round(float(self.id_String), 6)

    @property
    def begin_Coord(self):
        return self.__begin_Coord

    @property
    def end_Coord(self):
        return self.__end_Coord

    @property
    def n_Seg(self):
        return self.__n_Seg

    @property
    def nodes(self):
        return self.__nodeList

    @property
    def elements(self):
        return self.__elementList

    def addNode(self, node):
        self.__nodeList.append(node)

    def addElement(self, element):
        self.__elementList.append(element)

    @property
    def subElementID(self):
        return self.__id[3]

    def __createNode(self, sequenceNumber, node_cid):
        _node = Node(
            self.parent.eid,
            self.parent.parent.ringNumber,
            self.subElementID,
            sequenceNumber,
            node_cid,
            self,
            self.manager
        )
        self.addNode(_node)
        self.parent.addNode(_node)
        self.parent.parent.addNode(_node)
        self.manager.nodeManager.add(_node)
        return _node

    def __createBoltElement(self, sequenceNumber, cid, nodes):
        _boltElement = BoltElement(
            self.parent.eid,
            self.parent.parent.ringNumber,
            self.subElementID,
            sequenceNumber,
            cid,
            nodes,
            self,
            self.manager
        )
        self.addElement(_boltElement)
        self.parent.addElement(_boltElement)
        self.parent.parent.addElement(_boltElement)
        self.manager.elementManager.add(_boltElement)
        return _boltElement

    def createBolt(self):
        cid = it.structure.maxid() + 1
        node_cid = it.structure.node.maxid() + 1
        for i in range(self.n_Seg):
            if i == 0:
                _node1 = self.__createNode(1, node_cid)
                node_cid += 1
            _node2 = self.__createNode(i + 2, node_cid)
            node_cid += 1
            self.__createBoltElement(i + 1, cid, (_node1, _node2))
            cid += 1
            _node1 = _node2


# class BoltRingInstance(AbstractEntity):
#     def __init__(self, y_Coord, boltRing, parent, generator, manager):
#         super(BoltRingInstance, self).__init__(parent, generator, manager)
#         self.y_Coord = y_Coord
#         self.boltRing = boltRing
#         self.boltGroupInstanceList = []
#
#     def __repr__(self):
#         return 'BoltRing instance at Y={y_Coord}'.format(y_Coord=self.y_Coord)
#
#     @property
#     def ringNumber(self):
#         return self.boltRing._instances.index(self) + 1
#
#     def createBoltGroupInstance(self, boltGroup):
#         _boltGroupInstance = BoltGroupInstance(boltGroup, self, self.manager)
#         self.boltGroupInstanceList.append(_boltGroupInstance)
#         boltGroup._instances.append(_boltGroupInstance)
#         return _boltGroupInstance
#
#
# class BoltGroupInstance(AbstractEntity):
#     def __init__(self, boltGroup, parent, generator, manager):
#         super(BoltGroupInstance, self).__init__(parent, generator, manager)
#         self.boltGroup = boltGroup
#         self.boltEntityList = []
#
#     def __repr__(self):
#         return '{groupNumber}th bolt group instance at Y={y_Coord}'.format(
#             groupNumber=self.groupNumber,
#             y_Coord=self.parent.y_Coord
#         )
#
#     @property
#     def groupNumber(self):
#         return self.parnet.boltGroupInstanceList.index(self) + 1
#
#     def createBoltEntity(self):
#         _boltEntity = BoltEntity(self, self.manager)
#         self.boltEntityList.append(_boltEntity)
#         return _boltEntity