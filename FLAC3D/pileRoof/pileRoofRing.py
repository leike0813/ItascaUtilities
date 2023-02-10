# -*- coding: utf-8 -*-
import itasca as it
import numpy as np
import math
from ..customDecorators import *
from ..customFunctions import generatePropertyPhrase, generateRangePhrase
from ..model.abstractSubUtility import AbstractSubUtility
from pileRoofGroup import *
from .. import globalContainer as gc


__all__ = ['PileRoofRing']


class PileRoofRing(AbstractSubUtility):
    """
    PileRoofRing是管棚管理的第二级容器，代表“一环”管棚。
    PileRoofRing的参数有纵向坐标范围（y_Bound_Global）、长度（length）、搭接长度（overlapping）、外插角（angle）、单元划分数（n_Seg）、Structural element id（eid)和参数（propertyDict）。
    若要保证管棚末端与钢架连接，则还需指定钢架的structural element id(arch_id)，并令钢架节点与管棚末端节点坐标相同或接近。
    若不指定或id无效则默认约束管棚末端的绝对自由度。
    每个PileRoofRing包含若干个PileRoofGroup。
    """
    pileRoof_base_ID = gc.param['eid_base_offset'] + 50
    pileRoof_id_Offset = 1

    @classmethod
    def current_eid(cls):
        return cls.pileRoof_base_ID + cls.pileRoof_id_Offset

    def __init__(self, y_Bound_Global, length, spacing, angle, n_Seg, propertyDict, eid, util, arch_id = None):
        if eid == 'default':
            eid = PileRoofRing.current_eid()
            if PileRoofRing.pileRoof_id_Offset < 9:
                PileRoofRing.pileRoof_id_Offset += 1
            else:
                print(
                    """The maximum eid_offset of PileRoofRing is reached.
                    The eid of new PileRoofRing will not be increased automatically."""
                )
        super(PileRoofRing, self).__init__(util.modelUtil)
        self.__util = util
        self.length = length
        self.spacing = spacing
        self.angle = angle
        self.length_Proj = self.length * math.cos(math.radians(self.angle))
        self.n_Seg = n_Seg
        self.eid = eid
        self.arch_id = arch_id # 需要进行连接的拱架id
        self.propertyDict = propertyDict
        self.set_y_Bound_Global(y_Bound_Global)
        self.__pileRoofGroupList = []

    @property
    def util(self):
        return self.__util

    @y_Bound_Detect('y_Bound_Global')
    def set_y_Bound_Global(self, y_Bound_Global):
        self.y_Bound_Global = y_Bound_Global

    @property
    def n_PileRoofGroup(self):
        return len(self.__pileRoofGroupList)

    @property
    def pileRoofGroups(self):
        return tuple(self.__pileRoofGroupList)

    def newPileRoofGroup(self, angle_Bound, r_Spacing, origin, radius, offset):
        pileRoofGroup = PileRoofGroup(angle_Bound, r_Spacing, origin, radius, offset, self)
        self.__pileRoofGroupList.append(pileRoofGroup)
        return pileRoofGroup

    def newPileRoofGroup_Direct(self, nodeCoord = None, _symmetry = False):
        pileRoofGroup = PileRoofGroup_Direct(nodeCoord, _symmetry, self)
        self.__pileRoofGroupList.append(pileRoofGroup)
        return pileRoofGroup

    def applyPileRoof_Single(self, y_Coord, groups='All', _assignProp = False):
        for pr_gr in self.__pileRoofGroupList:
            pr_gr.applyPileRoof_Group(y_Coord)
        if _assignProp:
            it.command(
                'structure beam property {propertyPhrase} range {rangePhrase}'.format(
                    propertyPhrase=generatePropertyPhrase(self.propertyDict),
                    rangePhrase=generateRangePhrase(ypos=(y_Coord, y_Coord + self.length_Proj), id=self.eid)
                )
            )

    @y_Bound_Detect('y_Bound')
    def applyPileRoof_YRange_Ring(self, y_Bound, groups='All'):
        y_Bound = np.clip(y_Bound, self.y_Bound_Global[0], self.y_Bound_Global[1])
        cross_Range = np.array([int((y_Bound[0] - gc.param['geom_tol'] - self.y_Bound_Global[0]) // self.spacing),
                                int((y_Bound[1] - gc.param['geom_tol'] - self.y_Bound_Global[0]) // self.spacing)])
        n_Cross = cross_Range[1] - cross_Range[0]
        for i in range(n_Cross):
            self.applyPileRoof_Single((cross_Range[0] + i + 1) * self.spacing + self.y_Bound_Global[0], groups)
        if n_Cross > 0:
            it.command(
                'structure beam property {propertyPhrase} range {rangePhrase}'.format(
                    propertyPhrase=generatePropertyPhrase(self.propertyDict),
                    rangePhrase=generateRangePhrase(ypos=(y_Bound[0], y_Bound[1] + self.length_Proj), id=self.eid)
                )
            )

    @n_Step_Detect
    def applyPileRoof_Step_Ring(self, n_Step, groups='All'):
        self.applyPileRoof_YRange_Ring(self.modelUtil.excaUtil.y_BoundList[n_Step], groups)