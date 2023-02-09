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

    def newArchRing(self, y_Bound_Global, spacing, n_Seg, propertyDict, eid='default'):
        """
        增加新的ArchRing
        """
        archRing = ArchRing(y_Bound_Global, spacing, n_Seg, propertyDict, eid, self)
        self.addRing(archRing)
        return archRing

    def newArchRing_Direct(self, y_Bound_Global, spacing, n_Seg, propertyDict, nodeCoord=None, _symmetry=False, eid='default'):
        """
        增加新的ArchRing_Direct
        20220327：*已优化代码，ArchRing_Direct暂时保留以向后兼容。
        """
        archRing = ArchRing_Direct(y_Bound_Global, spacing, n_Seg, propertyDict, nodeCoord, _symmetry, eid, self)
        self.addRing(archRing)
        return archRing

    @staticmethod
    def applyArch_ByLine(beginPos, endPos, n_Seg, eid):
        it.command(
            'structure beam create by-line {positionPhrase} segments {_nseg} id {id}'.format(
                positionPhrase='{x0} {y0} {z0} {x1} {y1} {z1}'.format(
                    x0=beginPos[0], y0=beginPos[1], z0=beginPos[2],
                    x1=endPos[0], y1=endPos[1], z1=endPos[2]
                ),
                _nseg=n_Seg,
                id=eid
            )
        )

    @y_Bound_Detect('y_Bound')
    def applyArch_YRange(self, y_Bound):
        for a_r in self.rings:
            a_r.applyArch_YRange_Ring(y_Bound)

    @n_Step_Detect
    def applyArch_Step(self, n_Step):
        for a_r in self.rings:
            a_r.applyArch_YRange_Ring(self.modelUtil.excaUtil.y_BoundList[n_Step])