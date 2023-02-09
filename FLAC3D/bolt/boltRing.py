# -*- coding: utf-8 -*-
import itasca as it
import numpy as np
import types
from ..customDecorators import *
from ..customFunctions import generatePropertyPhrase, generateRangePhrase
from ..model.abstractRing import AbstractRing, AbstractRing_Instance
from boltGroup import *
from .. import globalContainer as gc


__all__ = ['BoltRing']


class BoltRing(AbstractRing):
    """
    BoltRing是锚杆管理的第二级容器，代表“一环”锚杆。
    BoltRing的参数有纵向坐标范围（y_Bound_Global）和间距（spacing）。
    每个BoltRing包含若干个BoltGroup，各BoltGroup的参数按其ID由其从属的BoltRing管理。
    """
    bolt_base_eid = gc.param['eid_base_offset'] + 0
    bolt_eid_Offset = 1

    @classmethod
    def current_eid(cls):
        return cls.bolt_base_eid + cls.bolt_eid_Offset

    def __init__(self, y_Bound_Global, spacing, eid, util):
        super(BoltRing, self).__init__(y_Bound_Global, {}, eid, util, BoltRing_Instance)
        self.spacing = spacing
        self.__boltEIDSet = set()

    def registerInstance(self, instance):
        _paramDict = {
            'n_Group': self.n_Group,
            'groups': self.groups,
            'propertyDict': self.propertyDict
        }
        instance.update_Param(_paramDict)

    def newBoltGroup(self, n_Seg, angle_Bound, n_Bolt, origin, inner_Radius, length, eid='default'):
        if eid == 'default':
            eid = BoltRing.current_eid()
            if BoltRing.bolt_eid_Offset < 29:
                BoltRing.bolt_eid_Offset += 1
            else:
                print(
                    """The maximum eid_offset of BoltGroup is reached.
                    The eid of new BoltGroup will not be increased automatically."""
                )
        boltGroup = BoltGroup(n_Seg, angle_Bound, n_Bolt, origin, inner_Radius, length, eid, self)
        self.addGroup(boltGroup)
        self.__boltEIDSet.add(eid)
        return boltGroup

    def newBoltGroup_Direct(self, n_Seg, nodeCoord = None, _symmetry = False, eid='default'):
        if eid == 'default':
            eid = BoltRing.current_eid()
            if BoltRing.bolt_eid_Offset < 29:
                BoltRing.bolt_eid_Offset += 1
            else:
                print(
                    """The maximum eid_offset of BoltGroup is reached.
                    The eid of new BoltGroup will not be increased automatically."""
                )
        boltGroup = BoltGroup_Direct(n_Seg, eid, nodeCoord, _symmetry, self)
        self.addGroup(boltGroup)
        self.__boltEIDSet.add(eid)
        return boltGroup

    def setBoltProperty(self, eid, propertyDict):
        self.propertyDict[eid] = propertyDict

    def applyBolt_Single(self, y_Coord, _assignProp = False):
        _instance = self.instantiate(self.modelUtil.entityManager.boltManager, y_Coord=y_Coord)
        for b_gr in self.groups:
            b_gr.applyBolt_Group(y_Coord, _instance)
        if _assignProp:
            for eid, _propDict in self.propertyDict.items():
                it.command(
                    'structure cable property {propertyPhrase} range {rangePhrase}'.format(
                       propertyPhrase=generatePropertyPhrase(_propDict),
                       rangePhrase=generateRangePhrase(ypos=y_Coord, id=eid)
                    )
                )

    def applyBolt_YRange_Ring(self, y_Bound):
        y_Bound = np.clip(y_Bound, self.y_Bound_Global[0], self.y_Bound_Global[1])
        cross_Range = np.array(
            [int((y_Bound[0] - gc.param['geom_tol'] - self.y_Bound_Global[0]) // self.spacing),
             int((y_Bound[1] - gc.param['geom_tol'] - self.y_Bound_Global[0]) // self.spacing)]
        )
        n_Cross = cross_Range[1] - cross_Range[0]
        for i in range(n_Cross):
            self.applyBolt_Single((cross_Range[1] - i) * self.spacing + self.y_Bound_Global[0])
        if n_Cross > 0:
            for eid, _propDict in self.propertyDict.items():
                it.command(
                    'structure cable property {propertyPhrase} range {rangePhrase}'.format(
                        propertyPhrase=generatePropertyPhrase(_propDict),
                        rangePhrase=generateRangePhrase(ypos=y_Bound, id=eid)
                    )
                )


class BoltRing_Instance(AbstractRing_Instance):
    def __init__(self, y_Coord, parent, generator, manager):
        super(BoltRing_Instance, self).__init__(y_Coord, parent, generator, manager)

    def __repr__(self):
        return 'BoltRing instance at Y={y_Coord}'.format(y_Coord=self.y_Coord)


# class BoltRing(AbstractGenerator, AbstractRing):
#     """
#     BoltRing是锚杆管理的第二级容器，代表“一环”锚杆。
#     BoltRing的参数有纵向坐标范围（y_Bound_Global）和间距（spacing）。
#     每个BoltRing包含若干个BoltGroup，各BoltGroup的参数按其ID由其从属的BoltRing管理。
#     """
#     bolt_base_eid = gc.param['eid_base_offset'] + 0
#     bolt_eid_Offset = 1
#
#     @classmethod
#     def current_eid(cls):
#         return cls.bolt_base_eid + cls.bolt_eid_Offset
#
#     def __new__(type, y_Bound_Global, spacing, eid, util):
#         return super(BoltRing, type).__new__(
#             type,
#             'BoltRing{sequenceNumber}'.format(sequenceNumber=util.n_Ring + 1),
#             (BoltRing_Instance,),
#             {}
#         )
#
#     def __init__(cls, y_Bound_Global, spacing, eid, util):
#         cls.__id = (eid, util.n_Ring + 1)
#         cls.__util = util
#         cls.spacing = spacing
#         cls.__groupList = []
#         cls.__boltEIDSet = set()
#         cls.__propertyDict = {}
#         cls.set_y_Bound_Global(y_Bound_Global)
#         super(BoltRing, cls).__init__(
#             util.modelUtil,
#             'BoltRing{sequenceNumber}'.format(sequenceNumber=util.n_Ring + 1),
#             (BoltRing_Instance, ),
#             {}
#         )
#
#     def __call__(cls, y_Coord, *args, **kwargs):
#         _instance = super(BoltRing, cls).__call__(parent=cls.modelUtil.entityManager.boltManager, *args, **kwargs)
#         _instance.initialize(y_Coord)
#         _paramDict = {
#             'n_Group': cls.n_Group,
#             'groups': cls.groups
#         }
#         _instance.update_Param(_paramDict)
#         return _instance
#
#     # @property
#     # def id_String(cls):
#     #     """以字符串形式返回自定义ID编码"""
#     #     return '{structuralElementID:0>3}{sequenceNumber:0>2}'.format(
#     #         structuralElementID=cls.__id[0],
#     #         sequenceNumber=cls.__id[1]
#     #     )
#     #
#     # sid = id_String
#     #
#     # @property
#     # def id(cls):
#     #     """以浮点数形式返回自定义ID编码"""
#     #     return int(cls.id_String)
#     #
#     # @property
#     # def sequenceNumber(cls):
#     #     return cls.__id[1]
#
#     @property
#     def util(cls):
#         return cls.__util
#
#     @y_Bound_Detect('y_Bound_Global')
#     def set_y_Bound_Global(cls, y_Bound_Global):
#         cls.y_Bound_Global = y_Bound_Global
#
#     @property
#     def n_Group(cls):
#         return len(cls.__groupList)
#
#     @property
#     def groups(cls):
#         return cls.__groupList
#
#     def newBoltGroup(cls, n_Seg, angle_Bound, n_Bolt, origin, inner_Radius, length, eid='default'):
#         if eid == 'default':
#             eid = BoltRing.current_eid()
#             if BoltRing.bolt_eid_Offset < 29:
#                 BoltRing.bolt_eid_Offset += 1
#             else:
#                 print(
#                     """The maximum eid_offset of BoltGroup is reached.
#                     The eid of new BoltGroup will not be increased automatically."""
#                 )
#         boltGroup = BoltGroup(n_Seg, angle_Bound, n_Bolt, origin, inner_Radius, length, eid, cls)
#         cls.__groupList.append(boltGroup)
#         cls.__boltEIDSet.add(eid)
#         return boltGroup
#
#     def newBoltGroup_Direct(cls, n_Seg, nodeCoord=None, _symmetry=False, eid='default'):
#         if eid == 'default':
#             eid = BoltRing.current_eid()
#             if BoltRing.bolt_eid_Offset < 29:
#                 BoltRing.bolt_eid_Offset += 1
#             else:
#                 print(
#                     """The maximum eid_offset of BoltGroup is reached.
#                     The eid of new BoltGroup will not be increased automatically."""
#                 )
#         boltGroup = BoltGroup_Direct(n_Seg, eid, nodeCoord, _symmetry, cls)
#         cls.__groupList.append(boltGroup)
#         cls.__boltEIDSet.add(eid)
#         return boltGroup
#
#     def setBoltProperty(cls, eid, propertyDict):
#         cls.propertyDict[eid] = propertyDict
#
#     def applyBolt_Single(cls, y_Coord, _assignProp=False):
#         _instance = cls.__call__(y_Coord=y_Coord)
#         for b_gr in cls.__groupList:
#             b_gr.applyBolt_Group(y_Coord, _instance)
#         if _assignProp:
#             for eid, _propDict in cls.propertyDict.items():
#                 it.command(
#                     'structure cable property {propertyPhrase} range {rangePhrase}'.format(
#                         propertyPhrase=generatePropertyPhrase(_propDict),
#                         rangePhrase=generateRangePhrase(ypos=y_Coord, id=eid)
#                     )
#                 )
#
#     def applyBolt_YRange_Ring(self, y_Bound):
#         y_Bound = np.clip(y_Bound, self.y_Bound_Global[0], self.y_Bound_Global[1])
#         cross_Range = np.array(
#             [int((y_Bound[0] - gc.param['geom_tol'] - self.y_Bound_Global[0]) // self.spacing),
#              int((y_Bound[1] - gc.param['geom_tol'] - self.y_Bound_Global[0]) // self.spacing)]
#         )
#         n_Cross = cross_Range[1] - cross_Range[0]
#         for i in range(n_Cross):
#             self.applyBolt_Single((cross_Range[1] - i) * self.spacing + self.y_Bound_Global[0])
#         if n_Cross > 0:
#             for eid, _propDict in self.propertyDict.items():
#                 it.command(
#                     'structure cable property {propertyPhrase} range {rangePhrase}'.format(
#                         propertyPhrase=generatePropertyPhrase(_propDict),
#                         rangePhrase=generateRangePhrase(ypos=y_Bound, id=eid)
#                     )
#                 )


# class BoltRing_Instance(AbstractEntity):
#     def initialize(self, y_Coord):
#         super(BoltRing_Instance, self).initialize()
#         self.__id = (self.generator.tid[0], self.generator.tid[1], self.generator.n_Instance)
#         self.y_Coord = y_Coord
#         self.__nodeList = []
#         self.__elementList = []
#
#     def __repr__(self):
#         return 'BoltRing instance at Y={y_Coord}'.format(y_Coord=self.y_Coord)
#
#     @property
#     def id_Tuple(self):
#         """以元组形式返回自定义ID编码"""
#         return self.__id
#
#     tid = id_Tuple
#
#     @property
#     def id_String(self):
#         """以字符串形式返回自定义ID编码"""
#         return '{structuralElementID:0>3}{sequenceNumber:0>2}.{instanceNubmer:0>3'.format(
#             structuralElementID=self.__id[0],
#             sequenceNumber=self.__id[1],
#             instanceNumber=self.__id[2]
#         )
#
#     sid = id_String
#
#     @property
#     def id(self):
#         """以浮点数形式返回自定义ID编码"""
#         return int(self.id_String)
#
#     @property
#     def sequenceNumber(self):
#         return self.__id[1]
#
#     @property
#     def instanceNumber(self):
#         return self.__id[2]
#
#     @property
#     def nodes(self):
#         return self.__nodeList
#
#     @property
#     def elements(self):
#         return self.__elementList
#
#     @property
#     def ringNumber(self):
#         return self.generator.instances.index(self) + 1
#
#     def addNode(self, node):
#         self.__nodeList.append(node)
#
#     def addElement(self, element):
#         self.__elementList.append(element)