# -*- coding: utf-8 -*-
import itasca as it
import math
from ..customFunctions import generateGroupRangePhrase, generatePropertyPhrase, generateRangePhrase
from abstractTBMComponent import AbstractTBMComponent
from .. import globalContainer as gc


__all__ = ['DiskGroup']

class DiskGroup(AbstractTBMComponent):
    base_ID = gc.param['id_base_offset'] + 90
    id_Offset = 1

    @classmethod
    def current_ID(cls):
        return cls.base_ID + cls.id_Offset

    def __init__(self, groupList, n_Disks, diameter, tipWidth, model_Area, propertyDict, _id, tbmUtil):
        if _id == 'default':
            _id = DiskGroup.current_ID()
            if DiskGroup.id_Offset < 7:
                DiskGroup.id_Offset += 1
            else:
                print(
                    """The maximum id_offset of DiskGroup is reached.
                    The id of new DiskGroup will not be increased automatically."""
                )
        super(DiskGroup, self).__init__(groupList, propertyDict, _id, tbmUtil)
        self.n_Disks = n_Disks
        self.diameter = diameter # DiskGroup的diameter是刀具自己的直径
        self.tipWidth = tipWidth
        self.model_Area = model_Area

    def __repr__(self):
        return 'D ' + str(self.diameter) + ' cutter disk'

    @property
    def radius(self):
        return self.diameter / 2

    @property
    def penetration(self):
        return self.tbmUtil.penetration

    @property
    def actual_Area(self):
        return self.tipWidth * math.sqrt(self.radius ** 2 - (self.radius - self.penetration) ** 2)

    @property
    def area_Ratio(self):
        return self.actual_Area / self.model_Area

    @property
    def cc(self):
        return math.tan(math.acos((self.radius - self.penetration) / self.radius) / 2)

    def applyDisk_Group(self, y_):
        # it.command(
        #     'structure liner create by-face id ' + str(self._id) \
        #     + ' group "__Disk_' + str(self._id) + '__" slot "__TBMUtil__" range group ' \
        #     + generateGroupRangePhrase(self.groupList) + ' position-y ' \
        #     + str(y_ - 100 * gc.param['geom_tol']) + ' ' + str(y_ + 100 * gc.param['geom_tol'])
        # )
        # it.command(
        #     'structure liner property ' + generatePropertyPhrase(self.propertyDict) \
        #     + ' range id ' + str(self._id) + ' group "__Disk_' + str(self._id) + '__" position-y ' \
        #     + str(y_ - 100 * gc.param['geom_tol']) + ' ' + str(y_ + 100 * gc.param['geom_tol'])
        # )
        it.command(
            'structure liner create by-face id {id} group {sourceGroup} slot {sourceSlot} range group {groupPhrase} {rangePhrase}'.format(
                id=self._id,
                sourceGroup='"__Disk_{id}__"'.format(id=self._id),
                sourceSlot='"__TBMUtil__"',
                groupPhrase=generateGroupRangePhrase(self.groupList),
                rangePhrase=generateRangePhrase(ypos=y_)
            )
        )
        it.command(
            'structure liner property {propertyPhrase} range group {groupPhrase} {rangePhrase}'.format(
                propertyPhrase=generatePropertyPhrase(self.propertyDict),
                groupPhrase='"__Disk_{id}__"'.format(id=self._id),
                rangePhrase=generateRangePhrase(
                    ypos=y_,
                    id=self._id
                )
            )
        )