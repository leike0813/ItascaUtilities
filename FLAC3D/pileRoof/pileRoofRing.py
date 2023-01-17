# -*- coding: utf-8 -*-
import itasca as it
import numpy as np
import math
from ..customDecorators import *
from ..customFunctions import generatePropertyPhrase, generateRangePhrase
from pileRoofGroup import *
from .. import globalContainer as gc


class PileRoofRing(object):
    """
    PileRoofRing是管棚管理的第二级容器，代表“一环”管棚。
    PileRoofRing的参数有纵向坐标范围（y_Bound_Global）、长度（length）、搭接长度（overlapping）、外插角（angle）、单元划分数（n_Seg）、ID（_id)和参数（propertyDict）。
    若要保证管棚末端与钢架连接，则还需指定钢架的structural element id(arch_id)，并令钢架节点与管棚末端节点坐标相同或接近。
    若不指定或id无效则默认约束管棚末端的绝对自由度。
    每个PileRoofRing包含若干个PileRoofGroup。
    """
    base_ID = gc.param['id_base_offset'] + 50
    id_Offset = 1

    @classmethod
    def current_ID(cls):
        return cls.base_ID + cls.id_Offset

    def __init__(self, y_Bound_Global, length, spacing, angle, n_Seg, propertyDict, _id, pileRoofUtil, arch_id = None):
        if _id == 'default':
            _id = PileRoofRing.current_ID()
            if PileRoofRing.id_Offset < 9:
                PileRoofRing.id_Offset += 1
            else:
                print(
                    """The maximum id_offset of PileRoofRing is reached.
                    The id of new PileRoofRing will not be increased automatically."""
                )
        self.pileRoofUtil = pileRoofUtil
        self.modelUtil = pileRoofUtil.modelUtil
        self.length = length
        self.spacing = spacing
        self.angle = angle
        self.length_Proj = self.length * math.cos(math.radians(self.angle))
        self.n_Seg = n_Seg
        self._id = _id
        self.arch_id = arch_id # 需要进行连接的拱架id
        self.propertyDict = propertyDict
        self.set_y_Bound_Global(y_Bound_Global)
        self.__pileRoofGroupList = []

    @y_Bound_Detect('y_Bound_Global')
    def set_y_Bound_Global(self, y_Bound_Global):
        self.y_Bound_Global = y_Bound_Global

    @property
    def n_PileRoofGroup(self):
        return len(self.__pileRoofGroupList)

    @property
    def pileRoofGroups(self):
        return self.__pileRoofGroupList

    def newPileRoofGroup(self, angle_Bound, r_Spacing, origin, radius, offset):
        pileRoofGroup = PileRoofGroup(angle_Bound, r_Spacing, origin, radius, offset, self)
        self.__pileRoofGroupList.append(pileRoofGroup)
        return pileRoofGroup

    def newPileRoofGroup_Direct(self, nodeCoord = None, _symmetry = False):
        pileRoofGroup = PileRoofGroup_Direct(nodeCoord, _symmetry, self)
        self.__pileRoofGroupList.append(pileRoofGroup)
        return pileRoofGroup

    def applyPileRoof_Ring(self, y_, _assignProp = False):
        for pr_gr in self.__pileRoofGroupList:
            pr_gr.applyPileRoof_Group(y_)
        if _assignProp:
            # it.command(
            #     'structure beam property ' + generatePropertyPhrase(self.propertyDict) + ' range position-y ' \
            #     + str(y_ - gc.param['geom_tol']) + ' ' + str(y_ + self.length_Proj + gc.param['geom_tol']) \
            #     + ' id ' + str(self._id)
            # )
            it.command(
                'structure beam property {propertyPhrase} range {rangePhrase}'.format(
                    propertyPhrase=generatePropertyPhrase(self.propertyDict),
                    rangePhrase=generateRangePhrase(ypos=(y_, y_ + self.length_Proj), id=self._id)
                )
            )

    def applyPileRoof_Coord_Ring(self, y_Bound):
        y_Bound = np.clip(y_Bound, self.y_Bound_Global[0], self.y_Bound_Global[1])
        cross_Range = np.array([int((y_Bound[0] - gc.param['geom_tol'] - self.y_Bound_Global[0]) // self.spacing), \
                                int((y_Bound[1] - gc.param['geom_tol'] - self.y_Bound_Global[0]) // self.spacing)])
        n_Cross = cross_Range[1] - cross_Range[0]
        for i in range(n_Cross):
            self.applyPileRoof_Ring((cross_Range[1] - i) * self.spacing + self.y_Bound_Global[0])
        if n_Cross > 0:
            # it.command(
            #     'structure beam property ' + generatePropertyPhrase(self.propertyDict) + ' range position-y ' \
            #     + str(y_Bound[0] - gc.param['geom_tol']) + ' ' + str(y_Bound[1] + self.length_Proj + gc.param['geom_tol']) \
            #     + ' id ' + str(self._id)
            # )
            it.command(
                'structure beam property {propertyPhrase} range {rangePhrase}'.format(
                    propertyPhrase=generatePropertyPhrase(self.propertyDict),
                    rangePhrase=generateRangePhrase(ypos=(y_Bound[0], y_Bound[1] + self.length_Proj), id=self._id)
                )
            )