# -*- coding: utf-8 -*-
import itasca as it
from vec import vec3
import math
from ..customDecorators import *
from ..customFunctions import generateRangePhrase, generateFixityPhrase
from ..model.abstractSubUtility import AbstractSubUtility
from pileRoofRing import PileRoofRing
from .. import globalContainer as gc


__all__ = ['PileRoofUtility']

class PileRoofUtility(AbstractSubUtility):
    """
    FLAC3D 6.0 管棚实用工具。
    拱架由PileRoofUtil的实例管理，并向下分为PileRoofRing——>PileRoofGroup。
    """

    def __init__(self, model=None):
        super(PileRoofUtility, self).__init__(model)
        self.__pileRoofRingList = []

    @property
    def n_PileRoofRing(self):
        return len(self.__pileRoofRingList)

    @property
    def pileRoofRings(self):
        return self.__pileRoofRingList

    def newPileRoofRing(self, y_Bound_Global, length, spacing, angle, n_Seg, propertyDict, _id='default', arch_id=None):
        pileRoofRing = PileRoofRing(y_Bound_Global, length, spacing, angle, n_Seg, propertyDict, _id, self, arch_id)
        self.__pileRoofRingList.append(pileRoofRing)
        return pileRoofRing

    @staticmethod
    def applyPileRoof_ByLine(beginPos, endPos, n_Seg, _id, arch_id=None):
        if arch_id:
            try:
                arch_node = it.structure.node.near(beginPos)
                if arch_node.id() == arch_id \
                        and (arch_node.pos() - vec3(beginPos)).mag() <= gc.param['geom_tol']:
                    _found_Node = True
                    arch_node_id = arch_node.component_id()
                else:
                    _found_Node = False
            except ValueError:
                _found_Node = False
        else:
            _found_Node = False
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
        if _found_Node:
            pile_node = it.structure.node.near(beginPos)
            # it.command(
            #     'structure link delete range id ' + str(_id) \
            #     + ' position-x ' + str(beginPos[0]) + ' position-y ' + str(beginPos[1]) + ' position-z ' + str(beginPos[2])
            # )
            # it.command(
            #     'structure link create on-nodeid ' + str(pile_node.component_id()) \
            #     + ' target node ' + str(arch_node_id)
            # )
            it.command(
                'structure link delete range {rangePhrase}'.format(
                    rangePhrase=generateRangePhrase(
                        xpos=beginPos[0],
                        ypos=beginPos[1],
                        zpos=beginPos[2],
                        id=_id
                    )
                )
            )
            it.command(
                'structure link create on-nodeid {_nodeid} target node {_target_nodeid}'.format(
                    _nodeid=pile_node.component_id(),
                    _target_nodeid=arch_node_id
                )
            )
        else:
            # it.command(
            #     'structure node fix velocity-x velocity-y velocity-z rotation-x rotation-y rotation-z range id ' \
            #     + str(_id) + ' position-x ' + str(beginPos[0]) + ' position-y ' + str(beginPos[1]) + ' position-z ' + str(beginPos[2])
            # )
            it.command(
                'structure node fix {fixityPhrase} range {rangePhrase}'.format(
                    fixityPhrase=generateFixityPhrase(mode='Encastre'),
                    rangePhrase=generateRangePhrase(
                        xpos=beginPos[0],
                        ypos=beginPos[1],
                        zpos=beginPos[2],
                        id=_id
                    )
                )
            )

    @y_Bound_Detect('y_Bound')
    def applyPileRoof_Coord(self, y_Bound):
        for pr_r in self.__pileRoofRingList:
            pr_r.applyPileRoof_Coord_Ring(y_Bound)

    @n_Step_Detect
    def applyPileRoof_Step(self, n_Step):
        for pr_r in self.__pileRoofRingList:
            pr_r.applyPileRoof_Coord_Ring(self.modelUtil.excaUtil.y_BoundList[n_Step])

    @staticmethod
    def propertyDictGenerator(pile_Diameter, pile_Thickness, steel_Density, steel_Young, grout_Density, grout_Young):
        inner_Diameter = pile_Diameter - 2 * pile_Thickness
        _EI_Total = (math.pi / 64) \
                    * (pile_Diameter ** 4 * steel_Young \
                       + inner_Diameter ** 4 * (grout_Young - steel_Young))
        _A_Total = math.pi * pile_Diameter ** 2 / 4
        _E = ((math.pi / 4) * (pile_Diameter ** 2 * steel_Young \
                               + inner_Diameter ** 2 * (grout_Young - steel_Young))) \
             / _A_Total
        _d = ((math.pi / 4) * (pile_Diameter ** 2 * steel_Density \
                               + inner_Diameter ** 2 * (grout_Density - steel_Density))) \
             / _A_Total
        _I = _EI_Total / _E
        return {'density': _d, 'young': _E, 'cross-sectional-area': _A_Total, \
                'moi-y': _I, 'moi-z': _I, 'moi-polar': 2 * _I}