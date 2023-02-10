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

    def newArchRing(self, y_Bound_Global, spacing, propertyDict, eid='default'):
        """
        增加新的ArchRing
        """
        archRing = ArchRing(y_Bound_Global, spacing, propertyDict, eid, self)
        self.addRing(archRing)
        return archRing

    def newArchRing_Direct(self, y_Bound_Global, spacing, propertyDict, nodeCoord=None, _symmetry=False, eid='default'):
        """
        增加新的ArchRing_Direct
        20220327：*已优化代码，ArchRing_Direct暂时保留以向后兼容。
        """
        archRing = ArchRing_Direct(y_Bound_Global, spacing, propertyDict, nodeCoord, _symmetry, eid, self)
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

    @staticmethod
    def applyArch_ByNode(node1_id, node2_id, n_Seg, eid):
        it.command(
            'structure beam create by-nodeids {node1_id} {node2_id} segments {_nseg} id {id}'.format(
                node1_id=node1_id,
                node2_id=node2_id,
                _nseg=n_Seg,
                id=eid
            )
        )
        it.command(
            'structure node initialize position (0, 0, 0) add range component-id {node1_id} {node2_id}'.format(
                node1_id=node1_id,
                node2_id=node2_id
            )
        )

    @staticmethod
    def applyArch_ByNodeAndCoord(beginNode_id, endPos, n_Seg, eid):
        it.command(
            'structure node create {pos}'.format(pos=tuple(endPos))
        )
        _endNode_id = it.structure.node.maxid()
        ArchUtility.applyArch_ByNode(beginNode_id, _endNode_id, n_Seg, eid)
        #return _endNode_id

    @y_Bound_Detect('y_Bound')
    def applyArch_YRange(self, y_Bound, groups='All'):
        for a_r in self.rings:
            a_r.applyArch_YRange_Ring(y_Bound, groups)

    @n_Step_Detect
    def applyArch_Step(self, n_Step, groups='All'):
        for a_r in self.rings:
            a_r.applyArch_YRange_Ring(self.modelUtil.excaUtil.y_BoundList[n_Step], groups)