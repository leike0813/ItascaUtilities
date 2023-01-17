# -*- coding: utf-8 -*-
import itasca as it
import numpy as np
import math
from ..customFunctions import generateGroupRangePhrase, generateFixityPhrase, generateRangePhrase
from ..customDecorators import convert_Group_To_GroupList, n_Step_Detect
from ..model.abstractSubUtility import AbstractSubUtility
from shield import Shield
from diskGroup import DiskGroup
from cutterHead import CutterHead
from .. import globalContainer as gc


__all__ = ['TBMUtility']

class TBMUtility(AbstractSubUtility):
    def __init__(self, model=None):
        super(TBMUtility, self).__init__(model)
        self.__currentStep = 0
        self.origin = None
        self.diameter = None
        self.penetration = None
        self.thrust = None
        self.shield = None
        self.cutterHead = None
        self.__diskGroupList = []

    @property
    def currentStep(self):
        return self.__currentStep

    def assignParameter(self, origin, diameter, penetration, thrust, _freezeDisp=False):
        self.origin = origin
        self.diameter = diameter
        self.penetration = penetration
        self.thrust = thrust
        self._freezeDisp = _freezeDisp

    @convert_Group_To_GroupList
    def newDiskGroup(self, groupName_or_List, n_Disks, diameter, tipWidth, model_Area, propertyDict, _id='default'):
        if self.n_DiskGroups == 0:
            it.fish.set('disk_Torque', 0.0)
        self.__diskGroupList.append(
            DiskGroup(groupName_or_List, n_Disks, diameter, tipWidth, model_Area, propertyDict, _id, self))

    @convert_Group_To_GroupList
    def setCutterHead(
            self, groupName_or_List, cutterHeight, frictionCoef, propertyDict, _id='default', origin=None, diameter=None
    ):
        self.cutterHead = CutterHead(
            groupName_or_List, origin, diameter, cutterHeight, frictionCoef, propertyDict, _id, self
        )
        it.fish.set('cutterHead_Torque', 0.0)
        it.fish.set('cutterHead_Thrust', 0.0)

    @convert_Group_To_GroupList
    def setShield(
            self, groupName_or_List, lengthCoef, preserveDisp, frictionCoef, propertyDict, _id='default', origin=None, diameter=None
    ):
        self.shield = Shield(
            groupName_or_List, origin, diameter, lengthCoef, preserveDisp, frictionCoef, propertyDict, _id, self
        )
        it.fish.set('shield_Thrust', 0.0)

    @property
    def n_DiskGroups(self):
        return len(self.__diskGroupList)

    @property
    def diskGroups(self):
        return self.__diskGroupList

    @property
    def diskActualArea_Total(self):
        _area = 0
        for dg in self.__diskGroupList:
            _area += dg.n_Disks * dg.actual_Area
        return _area

    @property
    def thrust_Apply_Area(self):
        return self.diskActualArea_Total + self.cutterHead.area if self.cutterHead != None else self.diskActualArea_Total

    @property
    def radius(self):
        return self.diameter / 2

    def applyDisks(self, y_):
        for dg in self.__diskGroupList:
            dg.applyDisk_Group(y_)
        # it.command(
        #     'structure node fix velocity-x velocity-y velocity-z rotation-x rotation-y rotation-z range group ' \
        #     + generateGroupRangePhrase(['__Disk_' + str(dg._id) + '__' for dg in self.diskGroups]) \
        #     + ' position-y ' + str(y_ - 100 * gc.param['geom_tol']) + ' ' + str(y_ + 100 * gc.param['geom_tol'])
        # )
        it.command(
            'structure node fix {fixityPhrase} range group {groupPhrase} {rangePhrase}'.format(
                fixityPhrase=generateFixityPhrase(mode='Encastre'),
                groupPhrase=generateGroupRangePhrase(
                    ['__Disk_{dg_id}__'.format(dg_id=dg._id) for dg in self.diskGroups]
                ),
                rangePhrase=generateRangePhrase(ypos=y_)
            )
        )

    def removeDisks(self, y_):
        # it.command(
        #     'structure liner delete range group ' \
        #     + generateGroupRangePhrase(['__Disk_' + str(dg._id) + '__' for dg in self.diskGroups]) \
        #     + ' position-y ' + str(y_ - 100 * gc.param['geom_tol']) + ' ' + str(y_ + 100 * gc.param['geom_tol'])
        # )
        it.command(
            'structure liner delete range group {groupPhrase} {rangePhrase}'.format(
                groupPhrase=generateGroupRangePhrase(
                    ['__Disk_{dg_id}__'.format(dg_id=dg._id) for dg in self.diskGroups]
                ),
                rangePhrase=generateRangePhrase(ypos=y_)
            )
        )

    @n_Step_Detect
    def applyTBM_Step(self, n_Step):
        if self.n_DiskGroups > 0:
            self.applyDisks(self.modelUtil.excaUtil.y_BoundList[n_Step][1])
            self.removeDisks(self.modelUtil.excaUtil.get_Y_Bound(n_Step - 1)[1])
        if self.cutterHead != None:
            if self._freezeDisp:
                self.cutterHead.freezeExcaFaceDisp_Step(n_Step)
            self.cutterHead.applyCutterHead(self.modelUtil.excaUtil.y_BoundList[n_Step][1])
            self.cutterHead.removeCutterHead(self.modelUtil.excaUtil.get_Y_Bound(n_Step - 1)[1])
        if self.shield != None:
            if self._freezeDisp:
                self.shield.freezeExcaBoundDisp_Step(n_Step)
            self.shield.applyShield_Coord(self.modelUtil.excaUtil.y_BoundList[n_Step])
            self.shield.removeShield_Coord(self.modelUtil.excaUtil.get_Y_Bound(n_Step - self.shield.lengthCoef))
        self.__currentStep = n_Step

    @property
    def disk_Torque(self):
        _thrust = (self.thrust / 2) if self.modelUtil.modelType == gc.ModelType.half_model else self.thrust
        _thrust_Uni = _thrust / self.thrust_Apply_Area if self.thrust_Apply_Area > 0 else 0.0
        disk_Torque_ = 0
        for dg in self.diskGroups:
            dg_Pressure = 0
            for el in it.structure.list():
                if el.in_group('__Disk_' + str(dg._id) + '__'):
                    el_Pressure = -(sum(el.normal_stress()) / 3) * el.area() * dg.area_Ratio  # 模型计算得到的单元正应力(反号，压力为正)
                    el_Pressure_Thrust = _thrust_Uni * el.area() * dg.area_Ratio if el_Pressure > 0 else 0.0  # 推力导致的单元正应力
                    el_Arm = math.sqrt(
                        (el.pos()[0] - self.origin[0]) ** 2 + (el.pos()[2] - self.origin[1]) ** 2)  # 单元力臂
                    dg_Pressure += (el_Pressure + el_Pressure_Thrust) * el_Arm
            disk_Torque_ += dg_Pressure * dg.cc
        return disk_Torque_ * 2 if self.modelUtil.modelType == gc.ModelType.half_model else disk_Torque_

    @property
    def cutterHead_Torque(self):
        _thrust = (self.thrust / 2) if self.modelUtil.modelType == gc.ModelType.half_model else self.thrust
        _thrust_Uni = _thrust / self.thrust_Apply_Area if self.thrust_Apply_Area > 0 else 0.0
        # _nStress = []
        # _area = []
        # _pos_X = []
        # _pos_Z = []
        cutterHead_Torque_ = 0
        for el in it.structure.list():
            if el.in_group('__CutterHead__'):
                el_Pressure = -(sum(el.normal_stress()) / 3) * el.area()
                el_Pressure_Thrust = _thrust_Uni * el.area() if el_Pressure > 0 else 0.0
                el_Arm = math.sqrt(
                    (el.pos()[0] - self.cutterHead.origin[0]) ** 2 + (el.pos()[2] - self.cutterHead.origin[1]) ** 2)
                cutterHead_Torque_ += (el_Pressure + el_Pressure_Thrust) * el_Arm
        #        _nStress.append(sum(el.normal_stress()) / 3)
        #        _area.append(el.area())
        #        _pos_X.append(el.pos()[0])
        #        _pos_Z.append(el.pos()[2])
        # cutterHead_Torque_ = (-1) * self.cutterHead.frictionCoef \
        #    * np.sum((np.array(_nStress) - _thrust_Uni) * np.array(_area) \
        #             * np.sqrt((np.array(_pos_X) - self.cutterHead.origin[0]) ** 2 \
        #                       + (np.array(_pos_Z) - self.cutterHead.origin[1]) ** 2))
        return cutterHead_Torque_ * 2 if self.modelUtil.modelType == gc.ModelType.half_model else cutterHead_Torque_

    @property
    def cutterHead_Thrust(self):
        cutterHead_Thrust_ = 0
        for el in it.structure.list():
            if el.in_group('__CutterHead__'):
                el_Pressure = -(sum(el.normal_stress()) / 3) * el.area()
                cutterHead_Thrust_ += el_Pressure
        return cutterHead_Thrust_ * 2 if self.modelUtil.modelType == gc.ModelType.half_model else cutterHead_Thrust_

    @property
    def shield_Thrust(self):
        _nStress = []
        _area = []
        for el in it.structure.list():
            if el.in_group('__Shield__'):
                _nStress.append(sum(el.normal_stress()) / 3)
                _area.append(el.area())
        shield_Thrust_ = np.sum(np.array(_nStress) * np.array(_area)) * self.shield.frictionCoef * (-1)
        return shield_Thrust_ * 2 if self.modelUtil.modelType == gc.ModelType.half_model else shield_Thrust_

    def getTorqueAndThrust(self, dummy):
        disk_Torque = self.disk_Torque if self.n_DiskGroups > 0 else 0.0
        cutterHead_Torque = self.cutterHead_Torque if self.cutterHead != None else 0.0
        cutterHead_Thrust = self.cutterHead_Thrust if self.cutterHead != None else 0.0
        shield_Thrust = self.shield_Thrust if self.shield != None else 0.0
        it.fish.set('disk_Torque', disk_Torque)
        it.fish.set('cutterHead_Torque', cutterHead_Torque)
        it.fish.set('cutterHead_Thrust', cutterHead_Thrust)
        it.fish.set('shield_Thrust', shield_Thrust)