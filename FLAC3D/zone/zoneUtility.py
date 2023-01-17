# -*- coding: utf-8 -*-
import itasca as it
from itasca import zonearray as za
import numpy as np
import math
from ..customDecorators import *
from ..customFunctions import generatePropertyPhrase
from ..model.abstractSubUtility import AbstractSubUtility
from ..material.materialSlot import MaterialSlot


__all__ = ['ZoneUtility']

class ZoneUtility(AbstractSubUtility):
    def __init__(self, model=None):
        super(ZoneUtility, self).__init__(model)
        self.__materialSlotList = []

    @property
    def count(self):
        return it.zone.count()

    @property
    def pos(self):
        return za.pos()

    @property
    def pos_x(self):
        return za.pos().T[0]

    @property
    def pos_y(self):
        return za.pos().T[1]

    @property
    def pos_z(self):
        return za.pos().T[2]

    @property
    def n_MaterialSlots(self):
        return len(self.__materialSlotList)

    @property
    def materialSlots(self):
        return {ms.slotName: ms for ms in self.__materialSlotList}

    @property
    def materialSlotList(self):
        return [ms.slotName for ms in self.__materialSlotList]

    @property
    def gridPoints(self):
        gpSet = set()
        zoneGPArray = za.gridpoints()
        for i in range(zoneGPArray.shape[0]):
            gpSet.update(list(zoneGPArray[i]))
        return np.array(sorted(list(gpSet)))

    def gridPoints_Group(self, groupName, _returnSet=False):
        gpSet = set()
        groupMask = za.in_group(groupName, 'any')
        groupGPArray = za.gridpoints()[groupMask]
        for i in range(groupGPArray.shape[0]):
            gpSet.update(list(groupGPArray[i]))
        return np.array(sorted(list(gpSet))) if not _returnSet else gpSet

    def gridPoints_Group_Union(self, groupNameList, _returnSet=False):
        gpSet_Union = set()
        groupMaskList = [za.in_group(groupName, 'any') for groupName in groupNameList]
        groupMask_Union = groupMaskList[0]
        for i in range(1, len(groupNameList)):
            groupMask_Union = np.logical_or(groupMask_Union, groupMaskList[i])
        groupGPArray_Union = za.gridpoints()[groupMask_Union]
        for i in range(groupGPArray_Union.shape[0]):
            gpSet_Union.update(list(groupGPArray_Union[i]))
        return np.array(sorted(list(gpSet_Union))) if not _returnSet else gpSet_Union

    def gridPoints_Group_Intersect(self, groupNameList, _returnSet=False):
        gpSetList = [self.gridPoints_Group(groupName, _returnSet=True) for groupName in groupNameList]
        gpSet_Intersect = gpSetList[0]
        for i in range(1, len(groupNameList)):
            gpSet_Intersect.intersection_update(gpSetList[i])
        return np.array(sorted(list(gpSet_Intersect))) if not _returnSet else gpSet_Intersect

    def bounding_Group(self, groupName, direction=2):  # direction = 0, 1, 2 denotes x, y, z axis respectively.
        gpIndArray = self.gridPoints_Group(groupName)
        if direction == 0:
            gp_pos = self.modelUtil.gpUtil.pos_x
        elif direction == 1:
            gp_pos = self.modelUtil.gpUtil.pos_y
        elif direction == 2:
            gp_pos = self.modelUtil.gpUtil.pos_z
        bounding = [gp_pos[gpIndArray].min(), gp_pos[gpIndArray].max()]
        return tuple(bounding)

    def newMaterialSlot(self, slotName):
        materialSlot = MaterialSlot(slotName, self)
        self.__materialSlotList.append(materialSlot)
        return materialSlot

    @staticmethod
    def assignMaterial(cModel, propertyDict, range_):
        # it.command('zone cmodel assign ' + cModel + ' range ' + range_)
        it.command('zone cmodel assign {cmodel} range {rangePhrase}'.format(
            cmodel=cModel,
            rangePhrase=range_
        ))
        if cModel.lower() != 'null':
            # it.command('zone property ' + generatePropertyPhrase(propertyDict) + ' range ' + range_)
            it.command('zone property {propertyPhrase} range {rangePhrase}'.format(
                propertyPhrase=generatePropertyPhrase(propertyDict),
                rangePhrase=range_
            ))

    @staticmethod
    @convert_Group_To_GroupList
    def assignMaterial_CamClay(groupName_or_List, propertyDict,
                               p_r=1e3):  # _poisson, _friction, _Cc, _Cs, _e0, _cu, _OCR, p_r = 1e3):
        """
        默认量纲为N、m，参考压力为1kPa。
        propertyDict键名称：'poisson','friction','Cc','Cs','e0','cu','OCR'
        """
        _M = 6 * math.sin(math.radians(propertyDict['friction'])) / (
                    3 - math.sin(math.radians(propertyDict['friction'])))
        _v0 = 1 + propertyDict['e0']
        _lambda = propertyDict['Cc'] / math.log(10)
        _kappa = propertyDict['Cs'] / math.log(10)
        _cu = propertyDict['cu']
        v_r = (_v0 + _lambda * math.log(2 * _cu / (_M * p_r)) + (_lambda - _kappa) * math.log(2)) if _cu > 0 else _v0
        _OCR = propertyDict['OCR']
        _poisson = propertyDict['poisson']
        for groupName in groupName_or_List:
            for z in it.zone.list():
                if z.in_group(groupName):
                    z_stress_effecitve = z.stress_effective()
                    z_p = (-1) * z_stress_effecitve.trace() / 3
                    z_q = math.sqrt(3 * z_stress_effecitve.j2())
                    pc_r = z_p * (1 + (z_q / (z_p * _M)) ** 2) * _OCR
                    v_min = v_r - _lambda * math.log(pc_r / p_r) + _kappa * math.log(pc_r / z_p * 5)
                    K_max = v_min * z_p * 5 / _kappa
                    z.set_model('modified-cam-clay')
                    z.set_prop('bulk-maximum', K_max)
                    z.set_prop('kappa', _kappa)
                    z.set_prop('lambda', _lambda)
                    z.set_prop('poisson', _poisson)
                    z.set_prop('pressure-reference', p_r)
                    z.set_prop('pressure-effective', z_p)
                    z.set_prop('pressure-preconsolidation', pc_r)
                    z.set_prop('ratio-critical-state', _M)
                    z.set_prop('specific-volume-reference', v_r)

    def assignModelMaterials_BySlot(self, slotName):
        self.materialSlots[slotName].assignMaterials('')