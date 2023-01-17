# -*- coding: utf-8 -*-
from ..gridPoint.gridPointUtility import GridPointUtility
from ..zone.zoneUtility import ZoneUtility
from ..material.materialUtility import MaterialUtility
from ..arch.archUtility import ArchUtility
from ..bolt.boltUtility import BoltUtility
from ..pileRoof.pileRoofUtility import PileRoofUtility
from ..excavation.excavationUtility import ExcavationUtility
from ..tbm.tbmUtility import TBMUtility
from modelEntityManager import ModelEntityManager
from ..customFunctions import generateRangePhrase
from .. import globalContainer as gc
import itasca as it
from itasca import zonearray as za
from itasca import gridpointarray as gpa
import numpy as np
import dill
import math


__all__ = ['ModelUtility']

class ModelUtility(object):
    _instance = None
    def __new__(cls, new = False, *args, **kw):
        '''
        令ModelUtility成为singleton
        '''
        if new or cls._instance is None:
            cls._instance = object.__new__(cls, new, *args, **kw)
        return cls._instance

    def __init__(self, type_ = gc.ModelType.full_Model, new = False):
        self.__type = type_
        self.gpUtil = GridPointUtility(self)
        self.zoneUtil = ZoneUtility(self)
        self.materialUtil = MaterialUtility(self)
        self.archUtil = ArchUtility(self)
        self.boltUtil = BoltUtility(self)
        self.pileRoofUtil = PileRoofUtility(self)
        self.excaUtil = ExcavationUtility(self)
        self.tbmUtil = TBMUtility(self)
        self.entityManager = ModelEntityManager(self)

    def save(self):
        """已弃用"""
        it.fish.set('__ModelUtility__', dill.dumps(self))

    @staticmethod
    def load():
        """已弃用"""
        # if '_save_Model' not in it.state_callbacks()['save']:
        #     it.set_callback('_save_Model', 'save')
        # if ModelUtility._instance is None:
        #     ModelUtility._instance = dill.loads(it.fish.get('__ModelUtility__'))
        return ModelUtility._instance

    @property
    def modelType(self):
        return self.__type

    @modelType.setter
    def modelType(self, type_ ):
        if type_ != 1 and type_ != 0:
            raise ValueError
        self.__type = type_

    def initStress(self, slotName, burdenStress, laterialCoef_x = None, laterialCoef_y = None):
        '''
        自动根据MaterialSlots中的材料参数（密度）和输入的覆土重度计算初始应力并赋予模型。
        可分别指定x向和y向的侧压力系数
        *未来可添加自由指定主应力方向的算法
        '''
        # it.command(
        #     'zone face apply stress-normal ' + str(burdenStress) +' range position-z ' + str(self.gpUtil.bounding_z[1])
        # )
        it.command(
            'zone face apply stress-normal {burdenStress} range {rangePhrase}'.format(
                burdenStress=burdenStress,
                rangePhrase=generateRangePhrase(zpos=self.gpUtil.bounding_z[1])
            )
        )
        groupBound_z = []
        groupNameSeq = []
        for groupName in self.zoneUtil.materialSlots[slotName].groupList:
            groupNameSeq.append(groupName)
            groupBound_z.append(self.zoneUtil.bounding_Group(groupName, direction=2))
        groupBound_z = np.array(groupBound_z)
        boundSort = groupBound_z.argsort(axis=0)
        if not np.all(boundSort[:, 0] == boundSort[:, 1]):
            return
        burdenStress_Accu = burdenStress
        zoneStress = za.stress_flat()
        zonePos_z = self.zoneUtil.pos_z
        surface_z = self.gpUtil.bounding_z[1]
        grav_z = it.gravity_z()
        for i in range(self.zoneUtil.materialSlots[slotName].n_Groups - 1, -1, -1):
            bound_ = groupBound_z[boundSort[i][0]]
            group_ = groupNameSeq[boundSort[i][0]]
            prop_ = self.zoneUtil.materialSlots[slotName].propertyDicts_Group[group_]
            groupMask = za.in_group(group_, 'any')
            if i != self.zoneUtil.materialSlots[slotName].n_Groups - 1:
                burdenStress_Accu = burdenStress_Prev + (bound_Prev - bound_[1]) * density_Prev * grav_z
            """#Useless. Reserve for future reuse.
            if 'young' in prop_.keys():
                E_ = prop_['young']
            elif 'bulk' in prop_.keys() and 'shear' in prop_.keys():
                K_, G_ = prop_['bulk'], prop_['shear']
                E_ = 9 * K_ * G_ / (3 * K_ + G_)
            """
            if laterialCoef_x == None:
                if 'friction' in prop_.keys():
                    laterialCoef_x = 1.0 - math.sin(math.radians(prop_['friction'])) / (
                                1.0 + math.sin(math.radians(prop_['friction'])))
                else:
                    laterialCoef_x = 1.0
            if laterialCoef_y == None:
                if 'friction' in prop_.keys():
                    laterialCoef_y = 1.0 - math.sin(math.radians(prop_['friction'])) / (
                                1.0 + math.sin(math.radians(prop_['friction'])))
                else:
                    laterialCoef_y = 1.0
            zoneStress[:, 2] += groupMask * (burdenStress_Accu + (bound_[1] - zonePos_z) * prop_['density'] * grav_z)
            zoneStress[:, 0] += groupMask * (zoneStress[:, 2] * laterialCoef_x)
            zoneStress[:, 1] += groupMask * (zoneStress[:, 2] * laterialCoef_y)
            burdenStress_Prev = burdenStress_Accu + (bound_[1] - bound_[0]) * prop_['density'] * grav_z
            bound_Prev = bound_[0]
            density_Prev = prop_['density']
        za.set_stress_flat(zoneStress)

    def resetDispAndVel(self):
        '''
        清空位移、速度和state记录
        '''
        zero_ = np.zeros((it.gridpoint.count(), 3))
        gpa.set_disp(zero_)
        gpa.set_vel(zero_)
        it.command('zone initialize state 0')