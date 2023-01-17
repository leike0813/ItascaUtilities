# -*- coding: utf-8 -*-
import itasca as it
import numpy as np
import math
from ..structuralComponent.node import Node
from bolt import *
from ..customFunctions import generateRangePhrase, generateFixityPhrase
from .. import globalContainer as gc


__all__ = ['BoltGroup', 'BoltGroup_Direct']

class BoltGroup_Abstract(object):
    """BoltGroup抽象基类，避免重复代码。"""
    def __init__(self, n_Seg, _id, boltRing):
        self.boltRing = boltRing
        self.boltUtil = boltRing.boltUtil
        self.modelUtil = boltRing.modelUtil
        self.n_Seg = n_Seg
        self._id = _id
        self._instances = []

    def applyBolt_Group(self, y_, parentInstance):
        _instance = parentInstance.createBoltGroupEntity(self)
        _cid = it.structure.maxid() + 1
        node_cid = it.structure.node.maxid() + 1
        for i in range(self.n_Bolts):
            self.boltUtil.applyBolt_ByLine(
                [self.nodeCoord[i][0][0], y_, self.nodeCoord[i][0][1]],
                [self.nodeCoord[i][1][0], y_, self.nodeCoord[i][1][1]],
                self.n_Seg,
                self._id
            )
            _bolt = _instance.createBoltEntity()
            for j in range(self.n_Seg):
                if j == 0:
                    _node1 = Node(
                        self._id, parentInstance.ringNumber, i + 1,
                        1, node_cid, _bolt, parentInstance.manager
                    )
                    self.modelUtil.entityManager.Node.add(_node1)
                    node_cid += 1
                _node2 = Node(
                    self._id, parentInstance.ringNumber, i + 1,
                    j + 2, node_cid, _bolt, parentInstance.manager
                )
                node_cid += 1
                self.modelUtil.entityManager.Node.add(_node2)
                _boltElement = _bolt.createBoltElement(
                    j + 1, _cid, (_node1, _node2)
                )
                _cid += 1
                self.modelUtil.entityManager.Element.add(_boltElement)
                _node1 = _node2


        if np.any(abs(self.modelUtil.gpUtil.bounding_y - y_) < gc.param['geom_tol']):
            # it.command(
            #     'structure node fix velocity-y rotation-x rotation-z range position-y ' \
            #     + str(y_ - gc.param['geom_tol']) + ' ' + str(y_ + gc.param['geom_tol']) + ' id ' + str(self._id)
            # )
            it.command(
                'structure node fix {fixityPhrase} range {rangePhrase}'.format(
                    fixityPhrase=generateFixityPhrase(mode='Y_Symm_Node'),
                    rangePhrase=generateRangePhrase(ypos=y_, id=self._id)
                )
            )


class BoltGroup(BoltGroup_Abstract):
    """
    BoltGroup是锚杆管理的基本单位，代表一组同规格的、等间距打设的锚杆。
    BoltGroup的参数有角度范围（angle_Bound）、数量（n_Bolts）、原点（origin）、内半径（inner_Radius）、长度（length）、单元划分数（n_Seg）、ID（_id）。
    """
    def __init__(self, n_Seg, angle_Bound, n_Bolts, origin, inner_Radius, length, _id, boltRing):
        super(BoltGroup, self).__init__(n_Seg, _id, boltRing)
        self.angle_Bound = angle_Bound
        self.n_Bolts = n_Bolts
        self.origin = origin
        self.inner_Radius = inner_Radius
        self.length = length
        self.angle_Spacing = (self.angle_Bound[1] - self.angle_Bound[0]) / (self.n_Bolts - 1)
        self.nodeCoord = np.array(
            [
                [
                    (
                        self.origin[0] + self.inner_Radius * math.sin(
                            math.radians(self.angle_Bound[0] + i * self.angle_Spacing)
                        ),
                        self.origin[1] + self.inner_Radius * math.cos(
                            math.radians(self.angle_Bound[0] + i * self.angle_Spacing)
                        )
                    ),
                    (
                        self.origin[0] + (self.inner_Radius + self.length) * math.sin(
                            math.radians(self.angle_Bound[0] + i * self.angle_Spacing)
                        ),
                        self.origin[1] + (self.inner_Radius + self.length) * math.cos(
                            math.radians(self.angle_Bound[0] + i * self.angle_Spacing)
                        )
                    )
                ] for i in range(self.n_Bolts)
            ]
        )

    def applyBolt_Group(self, y_, parentInstance):
        super(BoltGroup, self).applyBolt_Group(y_, parentInstance)
        if self.modelUtil.modelType == gc.ModelType.half_Model and \
                (min(self.angle_Bound) <= 0 or max(self.angle_Bound) >= 180):
            # it.command(
            #     'structure node fix velocity-z rotation-x rotation-y range position-x 0 position-y ' \
            #     + str(y_ - gc.param['geom_tol']) + ' ' + str(y_ + gc.param['geom_tol']) + ' id ' + str(self._id)
            # )
            it.command(
                'structure node fix {fixityPhrase} range {rangePhrase}'.format(
                    fixityPhrase=generateFixityPhrase(mode='Z_Symm_Node'),
                    rangePhrase=generateRangePhrase(xpos=0, ypos=y_, id=self._id)
                )
            )


class BoltGroup_Direct(BoltGroup_Abstract):
    """
    直接赋予锚杆节点坐标的BoltGroup。
    参数有节点坐标（nodeCoord）、单元划分数（n_Seg）、ID（_id）和对称性标志（_symmetry）。
    节点坐标（nodeCoord）必须是以浮点数（整数）为元素的三维可索引对象，其中第1维索引代表一根锚杆，第2维索引（0、1）代表起点和终点，第3维索引为坐标分量（x、z）。
    当对称性标志（_symmetry）为True时，添加锚杆后自动在x=0平面施加对称约束。
    """

    def __init__(self, n_Seg, nodeCoord, _symmetry, _id, boltRing):
        super(BoltGroup_Direct).__init__(n_Seg, _id, boltRing)
        self.nodeCoord = np.array(nodeCoord)
        self._symmetry = _symmetry and self.modelUtil.modelType == gc.ModelType.full_Model

    def applyBolt_Group(self, y_, parentInstance):
        self.n_Bolts = len(self.nodeCoord)
        super(BoltGroup, self).applyBolt_Group(y_, parentInstance)
        if self.modelUtil.modelType == gc.ModelType.half_Model:
            # it.command(
            #     'structure node fix velocity-z rotation-x rotation-y range position-x 0 position-y ' \
            #     + str(y_ - gc.param['geom_tol']) + ' ' + str(y_ + gc.param['geom_tol']) + ' id ' + str(self._id)
            # )
            it.command(
                'structure node fix {fixityPhrase} range {rangePhrase}'.format(
                    fixityPhrase=generateFixityPhrase(mode='Z_Symm_Node'),
                    rangePhrase=generateRangePhrase(xpos=0, ypos=y_, id=self._id)
                )
            )