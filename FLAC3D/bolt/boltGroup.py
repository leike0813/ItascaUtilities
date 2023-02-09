# -*- coding: utf-8 -*-
import itasca as it
import numpy as np
import math
import types
from bolt import *
from ..customFunctions import generateRangePhrase, generateFixityPhrase
from ..model.abstractGroup import AbstractGroup, AbstractGroup_Instance
from .. import globalContainer as gc


__all__ = ['BoltGroup', 'BoltGroup_Direct']


class BoltGroup_Abstract(AbstractGroup):
    """BoltGroup抽象基类，避免重复代码。"""
    def __init__(self, n_Seg, eid, ring):
        super(BoltGroup_Abstract, self).__init__(eid, ring, BoltGroup_Instance)
        self.n_Seg = n_Seg
        self.instantiate_Param_List = ['n_Seg', 'eid']

    def applyBolt_Group(self, y_Coord, parentInstance):
        _instance = self.instantiate(parentInstance, y_Coord=y_Coord)
        for i in range(self.n_Bolt):
            _bolt = _instance.createBoltEntity(i)
            self.util.applyBolt_ByLine(
                [self.nodeCoord[i][0][0], y_Coord, self.nodeCoord[i][0][1]],
                [self.nodeCoord[i][1][0], y_Coord, self.nodeCoord[i][1][1]],
                self.n_Seg,
                self.eid
            )
        if np.any(abs(self.modelUtil.gpUtil.bounding_y - y_Coord) < gc.param['geom_tol']):
            it.command(
                'structure node fix {fixityPhrase} range {rangePhrase}'.format(
                    fixityPhrase=generateFixityPhrase(mode='Y_Symm_Node'),
                    rangePhrase=generateRangePhrase(ypos=y_Coord, id=self.eid)
                )
            )


class BoltGroup(BoltGroup_Abstract):
    """
    BoltGroup是锚杆管理的基本单位，代表一组同规格的、等间距打设的锚杆。
    BoltGroup的参数有:
        角度范围（angle_Bound）: 2元素list-like，角度以degree输入
        数量（n_Bolt）：整数
        原点（origin）：2元素list-like，xOz平面坐标
        内半径（inner_Radius）：整数或浮点数
        长度（length）：整数或浮点数
        单元划分数（n_Seg）：整数
        Structural element id（eid）：整数
    """
    def __init__(self, n_Seg, angle_Bound, n_Bolt, origin, inner_Radius, length, eid, ring):
        super(BoltGroup, self).__init__(n_Seg, eid, ring)
        self.__angle_Bound = angle_Bound
        self.__n_Bolt = n_Bolt
        self.__origin = origin
        self.__inner_Radius = inner_Radius
        self.__length = length
        self.calculateNodeCoord()

    def registerInstance(self, instance):
        _paramDict = {
            'type': 'normal',
            'boltRing': self.ring,
            'nodeCoord': self.nodeCoord,
            'n_Bolt': self.n_Bolt,
            'angle_Bound': self.angle_Bound,
            'origin': self.origin,
            'inner_Radius': self.inner_Radius,
            'length': self.length,
            'angle_Spacing': self.angle_Spacing
        }
        instance.update_Param(_paramDict)

    @property
    def angle_Bound(self):
        return self.__angle_Bound

    @angle_Bound.setter
    def angle_Bound(self, value):
        self.__angle_Bound = value
        self.calculateNodeCoord()

    @property
    def n_Bolt(self):
        return self.__n_Bolt

    @n_Bolt.setter
    def n_Bolt(self, value):
        self.__n_Bolt = value
        self.calculateNodeCoord()

    @property
    def origin(self):
        return self.__origin

    @origin.setter
    def origin(self, value):
        self.__origin = value
        self.calculateNodeCoord()

    @property
    def inner_Radius(self):
        return self.__inner_Radius

    @inner_Radius.setter
    def inner_Radius(self, value):
        self.__inner_Radius = value
        self.calculateNodeCoord()

    @property
    def length(self):
        return self.__length

    @length.setter
    def length(self, value):
        self.__length = value
        self.calculateNodeCoord()

    @property
    def angle_Spacing(self):
        return self.__angle_Spacing

    def calculateNodeCoord(self):
        self.__angle_Spacing = (self.__angle_Bound[1] - self.__angle_Bound[0]) / (self.__n_Bolt - 1)
        self.setNodeCoord(np.array(
            [
                [
                    (
                        self.__origin[0] + self.__inner_Radius * math.sin(
                            math.radians(self.__angle_Bound[0] + i * self.__angle_Spacing)
                        ),
                        self.__origin[1] + self.__inner_Radius * math.cos(
                            math.radians(self.__angle_Bound[0] + i * self.__angle_Spacing)
                        )
                    ),
                    (
                        self.__origin[0] + (self.__inner_Radius + self.__length) * math.sin(
                            math.radians(self.__angle_Bound[0] + i * self.__angle_Spacing)
                        ),
                        self.__origin[1] + (self.__inner_Radius + self.__length) * math.cos(
                            math.radians(self.__angle_Bound[0] + i * self.__angle_Spacing)
                        )
                    )
                ] for i in range(self.__n_Bolt)
            ]
        ))

    def applyBolt_Group(self, y_Coord, parentInstance):
        super(BoltGroup, self).applyBolt_Group(y_Coord, parentInstance)
        if self.modelUtil.modelType == gc.ModelType.half_Model and \
                (min(self.__angle_Bound) <= 0 or max(self.__angle_Bound) >= 180):
            it.command(
                'structure node fix {fixityPhrase} range {rangePhrase}'.format(
                    fixityPhrase=generateFixityPhrase(mode='Z_Symm_Node'),
                    rangePhrase=generateRangePhrase(xpos=0, ypos=y_Coord, id=self.eid)
                )
            )


class BoltGroup_Direct(BoltGroup_Abstract):
    """
    直接赋予锚杆节点坐标的BoltGroup。
    参数有节点坐标（nodeCoord）、单元划分数（n_Seg）、Structural element id（eid）和对称性标志（_symmetry）。
    节点坐标（nodeCoord）必须是以浮点数（整数）为元素的三维可索引对象，其中第1维索引代表一根锚杆，第2维索引（0、1）代表起点和终点，第3维索引为坐标分量（x、z）。
    当对称性标志（_symmetry）为True时，添加锚杆后自动在x=0平面施加对称约束。
    """
    def __init__(self, n_Seg, nodeCoord, _symmetry, eid, ring):
        super(BoltGroup_Direct, self).__init__(n_Seg, eid, ring)
        self.setNodeCoord(nodeCoord)
        self._symmetry = _symmetry and self.modelUtil.modelType == gc.ModelType.full_Model
        self.instantiate_Param_List.append('_symmetry')

    def registerInstance(self, instance):
        _paramDict = {
            'type': 'direct',
            'boltRing': self.ring,
            'nodeCoord': self.nodeCoord,
            'n_Bolt': self.n_Bolt
        }
        instance.update_Param(_paramDict)

    @property
    def n_Bolt(self):
        return len(self.nodeCoord)

    def applyBolt_Group(self, y_Coord, parentInstance):
        super(BoltGroup_Direct, self).applyBolt_Group(y_Coord, parentInstance)
        if self.modelUtil.modelType == gc.ModelType.half_Model:
            # it.command(
            #     'structure node fix velocity-z rotation-x rotation-y range position-x 0 position-y ' \
            #     + str(y_Coord - gc.param['geom_tol']) + ' ' + str(y_Coord + gc.param['geom_tol']) + ' id ' + str(self.eid)
            # )
            it.command(
                'structure node fix {fixityPhrase} range {rangePhrase}'.format(
                    fixityPhrase=generateFixityPhrase(mode='Z_Symm_Node'),
                    rangePhrase=generateRangePhrase(xpos=0, ypos=y_Coord, id=self.eid)
                )
            )


class BoltGroup_Instance(AbstractGroup_Instance):
    def __init__(self, y_Coord, parent, generator, manager):
        super(BoltGroup_Instance, self).__init__(y_Coord, parent, generator, manager)

    def __repr__(self):
        return 'Bolt group instance at Y={y_Coord}'.format(y_Coord=self.y_Coord)

    def createBoltEntity(self, i):
        _boltEntity = BoltEntity(
            [self.nodeCoord[i][0][0], self.y_Coord, self.nodeCoord[i][0][1]],
            [self.nodeCoord[i][1][0], self.y_Coord, self.nodeCoord[i][1][1]],
            self.n_Seg,
            self,
            self.manager
        )
        self.addChild(_boltEntity)
        _boltEntity.createBolt() # 必须在注册boltEntity后执行以保证boltEntity的subElem_ID可正确返回
        return _boltEntity


# class BoltGroup_Abstract(AbstractGenerator, AbstractGroup):
#     """BoltGroup抽象基类，避免重复代码。"""
#
#     def initialize(cls, n_Seg, eid, ring):
#         cls.__id = (eid, ring.sequenceNumber, ring.n_Group + 1)
#         cls.__ring = ring
#         cls.__util = ring.util
#         cls.n_Seg = n_Seg
#         cls.eid = eid
#
#     @property
#     def ring(self):
#         return self.__ring
#
#     @property
#     def util(self):
#         return self.__util
#
#     def applyBolt_Group(self, y_Coord, parentInstance):
#         _instance = self.instantiate(parent=parentInstance, y_Coord=y_Coord)
#         for i in range(self.n_Bolt):
#             _bolt = _instance.createBoltEntity(i)
#             self.util.applyBolt_ByLine(
#                 [self.nodeCoord[i][0][0], y_Coord, self.nodeCoord[i][0][1]],
#                 [self.nodeCoord[i][1][0], y_Coord, self.nodeCoord[i][1][1]],
#                 self.n_Seg,
#                 self.eid
#             )
#         if np.any(abs(self.modelUtil.gpUtil.bounding_y - y_Coord) < gc.param['geom_tol']):
#             it.command(
#                 'structure node fix {fixityPhrase} range {rangePhrase}'.format(
#                     fixityPhrase=generateFixityPhrase(mode='Y_Symm_Node'),
#                     rangePhrase=generateRangePhrase(ypos=y_Coord, id=self.eid)
#                 )
#             )


# class BoltGroup(BoltGroup_Abstract):
#     """
#     BoltGroup是锚杆管理的基本单位，代表一组同规格的、等间距打设的锚杆。
#     BoltGroup的参数有角度范围（angle_Bound）、数量（n_Bolt）、原点（origin）、内半径（inner_Radius）、长度（length）、单元划分数（n_Seg）、Structural element id（eid）。
#     """
#     def __new__(type, n_Seg, angle_Bound, n_Bolt, origin, inner_Radius, length, eid, ring):
#         return super(BoltGroup, type).__new__(
#             type,
#             'BoltGroup{sequenceNumber}'.format(sequenceNumber=ring.n_Group + 1),
#             (BoltGroup_Instance,),
#             {}
#         )
#
#     def __init__(cls, n_Seg, angle_Bound, n_Bolt, origin, inner_Radius, length, eid, ring):
#         super(BoltGroup, cls).initialize(n_Seg, eid, ring)
#         cls.angle_Bound = angle_Bound
#         cls.n_Bolt = n_Bolt
#         cls.origin = origin
#         cls.inner_Radius = inner_Radius
#         cls.length = length
#         cls.angle_Spacing = (cls.angle_Bound[1] - cls.angle_Bound[0]) / (cls.n_Bolt - 1)
#         cls.nodeCoord = np.array(
#             [
#                 [
#                     (
#                         cls.origin[0] + cls.inner_Radius * math.sin(
#                             math.radians(cls.angle_Bound[0] + i * cls.angle_Spacing)
#                         ),
#                         cls.origin[1] + cls.inner_Radius * math.cos(
#                             math.radians(cls.angle_Bound[0] + i * cls.angle_Spacing)
#                         )
#                     ),
#                     (
#                         cls.origin[0] + (cls.inner_Radius + cls.length) * math.sin(
#                             math.radians(cls.angle_Bound[0] + i * cls.angle_Spacing)
#                         ),
#                         cls.origin[1] + (cls.inner_Radius + cls.length) * math.cos(
#                             math.radians(cls.angle_Bound[0] + i * cls.angle_Spacing)
#                         )
#                     )
#                 ] for i in range(cls.n_Bolt)
#             ]
#         )
#         super(BoltGroup, cls).__init__(
#             ring.modelUtil,
#             'BoltGroup{sequenceNumber}'.format(sequenceNumber=ring.n_Group + 1),
#             (BoltGroup_Instance,),
#             {}
#         )
#
#     def __call__(cls, y_Coord, parent, *args, **kwargs):
#         _instance = super(BoltGroup, cls).__call__(parent=parent, *args, **kwargs)
#         _instance.initialize(y_Coord)
#         _paramDict = {
#             'type': 'normal',
#             'boltRing': cls.ring
#         }
#         _instance.update_Param(_paramDict)
#         return _instance
#
#     def applyBolt_Group(cls, y_Coord, parentInstance):
#         super(BoltGroup, cls).applyBolt_Group(y_Coord, parentInstance)
#         if cls.modelUtil.modelType == gc.ModelType.half_Model and \
#                 (min(cls.angle_Bound) <= 0 or max(cls.angle_Bound) >= 180):
#             it.command(
#                 'structure node fix {fixityPhrase} range {rangePhrase}'.format(
#                     fixityPhrase=generateFixityPhrase(mode='Z_Symm_Node'),
#                     rangePhrase=generateRangePhrase(xpos=0, ypos=y_Coord, id=cls.eid)
#                 )
#             )


# class BoltGroup_Direct(BoltGroup_Abstract):
#     """
#     直接赋予锚杆节点坐标的BoltGroup。
#     参数有节点坐标（nodeCoord）、单元划分数（n_Seg）、Structural element id（eid）和对称性标志（_symmetry）。
#     节点坐标（nodeCoord）必须是以浮点数（整数）为元素的三维可索引对象，其中第1维索引代表一根锚杆，第2维索引（0、1）代表起点和终点，第3维索引为坐标分量（x、z）。
#     当对称性标志（_symmetry）为True时，添加锚杆后自动在x=0平面施加对称约束。
#     """
#     def __new__(type, n_Seg, nodeCoord, _symmetry, eid, ring):
#         return super(BoltGroup_Direct).__new__(
#             type,
#             'BoltGroup{sequenceNumber}'.format(sequenceNumber=ring.n_Group + 1),
#             (BoltGroup_Instance,),
#             {}
#         )
#
#     def __init__(cls, n_Seg, nodeCoord, _symmetry, eid, ring):
#         super(BoltGroup_Direct, cls).initialize(n_Seg, eid, ring)
#         cls.nodeCoord = np.array(nodeCoord)
#         cls._symmetry = _symmetry and cls.modelUtil.modelType == gc.ModelType.full_Model
#         super(BoltGroup_Direct, cls).__init__(
#             ring.modelUtil,
#             'BoltGroup{sequenceNumber}'.format(sequenceNumber=ring.n_Group + 1),
#             (BoltGroup_Instance,),
#             {}
#         )
#
#     def __call__(cls, y_Coord, parent, *args, **kwargs):
#         _instance = super(BoltGroup, cls).__call__(parent=parent, *args, **kwargs)
#         _instance.initialize(y_Coord)
#         _paramDict = {
#             'type': 'direct',
#             'boltRing': cls.ring,
#             'n_Bolt': cls.n_Bolt
#         }
#         _instance.update_Param(_paramDict)
#         return _instance
#
#     @property
#     def n_Bolt(cls):
#         return len(cls.nodeCoord)
#
#     def applyBolt_Group(cls, y_Coord, parentInstance):
#         super(BoltGroup_Direct, cls).applyBolt_Group(y_Coord, parentInstance)
#         if cls.modelUtil.modelType == gc.ModelType.half_Model:
#             it.command(
#                 'structure node fix {fixityPhrase} range {rangePhrase}'.format(
#                     fixityPhrase=generateFixityPhrase(mode='Z_Symm_Node'),
#                     rangePhrase=generateRangePhrase(xpos=0, ypos=y_Coord, id=cls.eid)
#                 )
#             )


# class BoltGroup_Instance(AbstractEntity):
#     def initialize(self, y_Coord):
#         super(BoltGroup_Instance, self).initialize()
#         self.__id = (
#             self.generator.tid[0],
#             self.generator.tid[1],
#             self.generator.tid[2],
#             self.parent.instanceNumber,
#             self.generator.n_Instance
#         )
#         self.y_Coord = y_Coord
#
#     def __repr__(self):
#         return 'Bolt group instance at Y={y_Coord}'.format(y_Coord=self.y_Coord)
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
#         return '{structuralElementID:0>3}{RingSequenceNumber:0>2}{sequenceNumber:0>2}.{RingInstanceNumber:0>3}{instanceNumber:0>3}'.format(
#             structuralElementID=self.__id[0],
#             RingSequenceNumber=self.__id[1],
#             sequenceNumber=self.__id[2],
#             RingInstanceNumber=self.__id[3],
#             instanceNumber=self.__id[4]
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
#         return self.__id[2]
#
#     @property
#     def instanceNumber(self):
#         return self.__id[4]
#
#     def createBoltEntity(self, i):
#         _boltEntity = BoltEntity(
#             [self.nodeCoord[i][0][0], self.y_Coord, self.nodeCoord[i][0][1]],
#             [self.nodeCoord[i][1][0], self.y_Coord, self.nodeCoord[i][1][1]],
#             self.n_Seg,
#             self,
#             self.manager
#         )
#         self.addChild(_boltEntity)
#         _boltEntity.createBolt() # 必须在注册boltEntity后执行以保证boltEntity的subElem_ID可正确返回
#         return _boltEntity

