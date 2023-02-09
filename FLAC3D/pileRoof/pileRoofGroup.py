# -*- coding: utf-8 -*-
import itasca as it
import numpy as np
import math
from ..customFunctions import generateRangePhrase, generateFixityPhrase
from ..model.abstractSubUtility import AbstractSubUtility
from .. import globalContainer as gc


__all__ = ['PileRoofGroup', 'PileRoofGroup_Direct']


class PileRoofGroup_Abstract(AbstractSubUtility):
    """ArchGroup抽象基类，避免重复代码。"""
    def __init__(self, ring):
        super(PileRoofGroup_Abstract, self).__init__(ring.modelUtil)
        self.__ring = ring
        self.__util = ring.util

    @property
    def ring(self):
        return self.__ring

    @property
    def util(self):
        return self.__util

    def applyPileRoof_Group(self, y_Coord, _symmConstrain):
        for i in range(self.n_Piles):
            self.util.applyPileRoof_ByLine(
                [self.nodeCoord[i][0][0], y_Coord, self.nodeCoord[i][0][2]],
                [self.nodeCoord[i][1][0], y_Coord + self.nodeCoord[i][1][1], self.nodeCoord[i][1][2]],
                self.ring.n_Seg,
                self.ring.eid,
                arch_id=self.ring.arch_id
            )
        if _symmConstrain:
            # it.command(
            #     'structure node fix velocity-x rotation-y rotation-z range position-x 0 position-y ' \
            #     + str(y_Coord - gc.param['geom_tol']) + ' ' + str(y_Coord + self.ring.length_Proj + gc.param['geom_tol']) \
            #     + ' id ' + str(self.ring.eid)
            # )
            it.command(
                'structure node fix {fixityPhrase} range {rangePhrase}'.format(
                    fixityPhrase=generateFixityPhrase(mode='X_Symm_Node'),
                    rangePhrase=generateRangePhrase(
                        xpos=0,
                        ypos=(y_Coord, y_Coord + self.ring.length_Proj),
                        id=self.ring.eid
                    )
                )
            )


class PileRoofGroup(PileRoofGroup_Abstract):
    """
    PileRoofGroup是管棚管理的基本单位，代表一环管棚中的一段。
    PileRoofGroup的参数有角度范围（angle_Bound）、原点（origin）、半径（radius）、环向间距（r_Spacing）和初始偏移距离（offset）。
    """
    def __init__(self, angle_Bound, r_Spacing, origin, radius, offset, ring):
        super(PileRoofGroup, self).__init__(ring)
        self.angle_Bound = angle_Bound
        self.origin = origin
        self.radius = radius
        self.offset = offset
        self.r_Spacing = r_Spacing
        self.angle_Offset = math.degrees(self.offset / self.radius)
        self.angle_Spacing = math.degrees(self.r_Spacing / self.radius)
        self.n_Piles = int((self.angle_Bound[1] - self.angle_Bound[0] - self.angle_Offset) // self.angle_Spacing) + 1
        self.angle_Residual = (self.angle_Bound[1] - self.angle_Bound[0] - self.angle_Offset) % self.angle_Spacing
        self.r_Spacing_Residual = self.angle_Residual * self.radius
        self.focal_Length = self.radius / math.tan(math.radians(self.ring.angle))
        _modulus = math.sqrt(self.focal_Length ** 2 + self.radius ** 2)
        _dir = [
            [
                self.radius * math.sin(
                    math.radians(self.angle_Offset + self.angle_Bound[0] + i * self.angle_Spacing)
                ) / _modulus,
                self.focal_Length / _modulus,
                self.radius * math.cos(
                    math.radians(self.angle_Offset + self.angle_Bound[0] + i * self.angle_Spacing)
                ) / _modulus
            ] for i in range(self.n_Piles)
        ]
        _start = [
            (
                self.origin[0] + self.radius * math.sin(
                    math.radians(self.angle_Offset + self.angle_Bound[0] + i * self.angle_Spacing)
                ),
                self.origin[1] + self.radius * math.cos(
                    math.radians(self.angle_Offset + self.angle_Bound[0] + i * self.angle_Spacing)
                )
            ) for i in range(self.n_Piles)
        ]
        self.nodeCoord = np.array(
            [
                [
                    [
                        _start[i][0], 0.0, _start[i][1]
                    ],
                    [
                        _start[i][0] + _dir[i][0] * self.ring.length,
                        _dir[i][1] * self.ring.length,
                        _start[i][1] + _dir[i][2] * self.ring.length
                    ]
                ] for i in range(self.n_Piles)
            ]
        )

    def applyPileRoof_Group(self, y_Coord):
        super(PileRoofGroup, self).applyPileRoof_Group(
            y_Coord,
            self.modelUtil.modelType == gc.ModelType.half_Model and \
            (
                    min(self.angle_Bound) + self.angle_Offset <= 0 or
                    max(self.angle_Bound) - self.angle_Residual >= 180
            )
        )


class PileRoofGroup_Direct(PileRoofGroup_Abstract):
    """
    直接赋予管棚节点坐标的PileRoofGroup。
    参数有节点坐标（nodeCoord）和对称性标志（_symmetry）。
    节点坐标（nodeCoord）必须是以浮点数（整数）为元素的三维可索引对象，其中第1维索引代表一根管棚，第2维索引（0、1）代表起点和终点，第3维索引为坐标分量（x、y、z）。
    当对称性标志（_symmetry）为True时，添加管棚后自动在x=0平面施加对称约束。
    """

    def __init__(self, nodeCoord, _symmetry, ring):
        super(PileRoofGroup_Direct, self).__init__(ring)
        self.nodeCoord = np.array(nodeCoord)
        self._symmetry = _symmetry and self.modelUtil.modelType == gc.ModelType.full_Model

    def applyPileRoof_Group(self, y_Coord):
        super(PileRoofGroup_Direct, self).applyPileRoof_Group(
            y_Coord,
            self.modelUtil.modelType == gc.ModelType.half_Model
        )
