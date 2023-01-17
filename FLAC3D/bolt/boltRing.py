# -*- coding: utf-8 -*-
import itasca as it
import numpy as np
from ..customDecorators import *
from ..customFunctions import generatePropertyPhrase, generateRangePhrase
from boltGroup import *
from .. import globalContainer as gc


class BoltRing(object):
    """
    BoltRing是锚杆管理的第二级容器，代表“一环”锚杆。
    BoltRing的参数有纵向坐标范围（y_Bound_Global）和间距（spacing）。
    每个BoltRing包含若干个BoltGroup，各BoltGroup的参数按其ID由其从属的BoltRing管理。
    """
    base_ID = gc.param['id_base_offset'] + 0
    id_Offset = 1

    @classmethod
    def current_ID(cls):
        return cls.base_ID + cls.id_Offset

    def __init__(self, y_Bound_Global, spacing, boltUtil):
        self.boltUtil = boltUtil
        self.modelUtil = boltUtil.modelUtil
        self.spacing = spacing
        self.__boltGroupList = []
        self.__boltIDSet = set()
        self.__boltPropertyDict = {}
        self.set_y_Bound_Global(y_Bound_Global)
        self._instances = []

    @y_Bound_Detect('y_Bound_Global')
    def set_y_Bound_Global(self, y_Bound_Global):
        self.y_Bound_Global = y_Bound_Global

    @property
    def n_BoltGroup(self):
        return len(self.__boltGroupList)

    @property
    def boltGroups(self):
        return self.__boltGroupList

    def newBoltGroup(self, n_Seg, angle_Bound, n_Bolts, origin, inner_Radius, length, _id='default'):
        if _id == 'default':
            _id = BoltRing.current_ID()
            if BoltRing.id_Offset < 29:
                BoltRing.id_Offset += 1
            else:
                print(
                    """The maximum id_offset of BoltGroup is reached.
                    The id of new BoltGroup will not be increased automatically."""
                )
        boltGroup = BoltGroup(n_Seg, angle_Bound, n_Bolts, origin, inner_Radius, length, _id, self)
        self.__boltGroupList.append(boltGroup)
        self.__boltIDSet.add(_id)
        return boltGroup

    def newBoltGroup_Direct(self, n_Seg, nodeCoord = None, _symmetry = False, _id='default'):
        if _id == 'default':
            _id = BoltRing.current_ID()
            if BoltRing.id_Offset < 29:
                BoltRing.id_Offset += 1
            else:
                print(
                    """The maximum id_offset of BoltGroup is reached.
                    The id of new BoltGroup will not be increased automatically."""
                )
        boltGroup = BoltGroup_Direct(n_Seg, _id, nodeCoord, _symmetry, self)
        self.__boltGroupList.append(boltGroup)
        self.__boltIDSet.add(_id)
        return boltGroup

    def setBoltProperty(self, _id, propertyDict):
        self.__boltPropertyDict[_id] = propertyDict

    def applyBolt_Ring(self, y_, _assignProp = False):
        _instance = self.modelUtil.entityManager.createBoltRingEntity(y_, self)
        for b_gr in self.__boltGroupList:
            b_gr.applyBolt_Group(y_, _instance)
        if _assignProp:
            for _id, _propDict in self.__boltPropertyDict.items():
                # it.command(
                #     'structure cable property ' + generatePropertyPhrase(_propDict) + ' range position-y ' \
                #     + str(y_ - gc.param['geom_tol']) + ' ' + str(y_ + gc.param['geom_tol']) + ' id ' + str(_id)
                # )
                it.command(
                    'structure cable property {propertyPhrase} range {rangePhrase}'.format(
                       propertyPhrase=generatePropertyPhrase(_propDict),
                       rangePhrase=generateRangePhrase(ypos=y_, id=_id)
                    )
                )

    def applyBolt_Coord_Ring(self, y_Bound):
        y_Bound = np.clip(y_Bound, self.y_Bound_Global[0], self.y_Bound_Global[1])
        cross_Range = np.array(
            [int((y_Bound[0] - gc.param['geom_tol'] - self.y_Bound_Global[0]) // self.spacing),
             int((y_Bound[1] - gc.param['geom_tol'] - self.y_Bound_Global[0]) // self.spacing)]
        )
        n_Cross = cross_Range[1] - cross_Range[0]
        for i in range(n_Cross):
            self.applyBolt_Ring((cross_Range[1] - i) * self.spacing + self.y_Bound_Global[0])
        if n_Cross > 0:
            for _id, _propDict in self.__boltPropertyDict.items():
                # it.command(
                #     'structure cable property ' + generatePropertyPhrase(_propDict) + ' range position-y ' \
                #     + str(y_Bound[0] - gc.param['geom_tol']) + ' ' + str(y_Bound[1] + gc.param['geom_tol']) + ' id ' + str(_id)
                # )
                it.command(
                    'structure cable property {propertyPhrase} range {rangePhrase}'.format(
                        propertyPhrase=generatePropertyPhrase(_propDict),
                        rangePhrase=generateRangePhrase(ypos=y_Bound, id=_id)
                    )
                )