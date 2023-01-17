# -*- coding: utf-8 -*-
import itasca as it
from ..customDecorators import *
from ..model.abstractSubUtility import AbstractSubUtility
from boltRing import BoltRing
from .. import globalContainer as gc


__all__ = ['BoltUtility']

class BoltUtility(AbstractSubUtility):
    """
    FLAC3D 6.0 锚杆实用工具。
    锚杆由BoltUtil的实例管理，并向下分为BoltRing——>BoltGroup。
    """

    def __init__(self, model=None):
        super(BoltUtility, self).__init__(model)
        self.__boltRingList = []

    @property
    def n_BoltRing(self):
        return len(self.__boltRingList)

    @property
    def boltRings(self):
        return self.__boltRingList

    def newBoltRing(self, y_Bound_Global, spacing):
        boltRing = BoltRing(y_Bound_Global, spacing, self)
        self.__boltRingList.append(boltRing)
        return boltRing

    @staticmethod
    def applyBolt_ByLine(beginPos, endPos, n_Seg, _id):
        # it.command(
        #     'structure cable create by-line ' + str(beginPos[0]) + ' ' + str(beginPos[1]) + ' ' + str(beginPos[2]) + ' ' \
        #     + str(endPos[0]) + ' ' + str(endPos[1]) + ' ' + str(endPos[2]) + ' segments ' + str(n_Seg) + ' id ' + str(_id)
        # )
        it.command(
            'structure cable create by-line {positionPhrase} segments {_nseg} id {_id}'.format(
                positionPhrase='{x0} {y0} {z0} {x1} {y1} {z1}'.format(
                    x0=beginPos[0], y0=beginPos[1], z0=beginPos[2],
                    x1=endPos[0], y1=endPos[1], z1=endPos[2]
                ),
                _nseg=n_Seg,
                _id=_id
            )
        )

    @y_Bound_Detect('y_Bound')
    def applyBolt_Coord(self, y_Bound):
        for b_r in self.__boltRingList:
            b_r.applyBolt_Coord_Ring(y_Bound)

    @n_Step_Detect
    def applyBolt_Step(self, n_Step):
        for b_r in self.__boltRingList:
            b_r.applyBolt_Coord_Ring(self.modelUtil.excaUtil.y_BoundList[n_Step])