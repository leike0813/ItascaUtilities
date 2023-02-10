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

    def newBoltRing(self, y_Bound_Global, spacing, id='default'):
        if id == 'default':
            id = 900
        boltRing = BoltRing(y_Bound_Global, spacing, id, self)
        self.addRing(boltRing)
        return boltRing

    @staticmethod
    def applyBolt_ByLine(beginPos, endPos, n_Seg, eid):
        it.command(
            'structure cable create by-line {positionPhrase} segments {_nseg} id {id}'.format(
                positionPhrase='{x0} {y0} {z0} {x1} {y1} {z1}'.format(
                    x0=beginPos[0], y0=beginPos[1], z0=beginPos[2],
                    x1=endPos[0], y1=endPos[1], z1=endPos[2]
                ),
                _nseg=n_Seg,
                id=eid
            )
        )

    @y_Bound_Detect('y_Bound')
    def applyBolt_YRange(self, y_Bound, groups='All'):
        for b_r in self.rings:
            b_r.applyBolt_YRange_Ring(y_Bound, groups)

    @n_Step_Detect
    def applyBolt_Step(self, n_Step, groups='All'):
        for b_r in self.rings:
            b_r.applyBolt_YRange_Ring(self.modelUtil.excaUtil.y_BoundList[n_Step], groups)