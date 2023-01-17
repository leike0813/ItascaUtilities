# -*- coding: utf-8 -*-
import itasca as it
from ..customDecorators import *
from ..model.abstractSubUtility import AbstractSubUtility
from archRing import *
from .. import globalContainer as gc


__all__ = ['ArchUtility']

class ArchUtility(AbstractSubUtility):
    """
    FLAC3D 6.0 拱架实用工具。
    拱架由ArchUtil的实例管理，并向下分为ArchRing——>ArchGroup。
    """

    def __init__(self, model=None):
        super(ArchUtility, self).__init__(model)
        self.__archRingList = []

    @property
    def n_ArchRing(self):
        return len(self.__archRingList)

    @property
    def archRings(self):
        return self.__archRingList

    def newArchRing(self, y_Bound_Global, spacing, n_Seg, propertyDict, _id='default'):
        """
        增加新的ArchRing
        """
        archRing = ArchRing(y_Bound_Global, spacing, n_Seg, propertyDict, _id, self)
        self.__archRingList.append(archRing)
        return archRing

    def newArchRing_Direct(self, y_Bound_Global, spacing, n_Seg, propertyDict, nodeCoord=None, _symmetry=False, _id='default'):
        """
        增加新的ArchRing_Direct
        20220327：*已优化代码，ArchRing_Direct暂时保留以向后兼容。
        """
        archRing = ArchRing_Direct(y_Bound_Global, spacing, n_Seg, propertyDict, nodeCoord, _symmetry, _id, self)
        self.__archRingList.append(archRing)
        return archRing

    @staticmethod
    def applyArch_ByLine(beginPos, endPos, n_Seg, _id):
        # it.command(
        #     'structure beam create by-line ' + str(beginPos[0]) + ' ' + str(beginPos[1]) + ' ' + str(beginPos[2]) + ' ' \
        #     + str(endPos[0]) + ' ' + str(endPos[1]) + ' ' + str(endPos[2]) + ' segments ' + str(n_Seg) + ' id ' + str(_id)
        # )
        it.command(
            'structure beam create by-line {positionPhrase} segments {_nseg} id {_id}'.format(
                positionPhrase='{x0} {y0} {z0} {x1} {y1} {z1}'.format(
                    x0=beginPos[0], y0=beginPos[1], z0=beginPos[2],
                    x1=endPos[0], y1=endPos[1], z1=endPos[2]
                ),
                _nseg=n_Seg,
                _id=_id
            )
        )

    @y_Bound_Detect('y_Bound')
    def applyArch_Coord(self, y_Bound):
        for a_r in self.__archRingList:
            a_r.applyArch_Coord_Ring(y_Bound)

    @n_Step_Detect
    def applyArch_Step(self, n_Step):
        for a_r in self.__archRingList:
            a_r.applyArch_Coord_Ring(self.modelUtil.excaUtil.y_BoundList[n_Step])