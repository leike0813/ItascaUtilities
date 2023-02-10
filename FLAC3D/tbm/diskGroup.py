# -*- coding: utf-8 -*-
import itasca as it
import math
from ..customFunctions import generateGroupRangePhrase, generatePropertyPhrase, generateRangePhrase
from abstractTBMComponent import AbstractTBMComponent
from .. import globalContainer as gc


__all__ = ['DiskGroup']

class DiskGroup(AbstractTBMComponent):
    base_eid = gc.param['eid_base_offset'] + 90
    eid_Offset = 1

    @classmethod
    def current_eid(cls):
        return cls.base_eid + cls.eid_Offset

    def __init__(self, rangeGroups, n_Disks, disk_Diameter, tipWidth, model_Area, propertyDict, eid, util):
        if eid == 'default':
            eid = DiskGroup.current_eid()
            if DiskGroup.eid_Offset < 7:
                DiskGroup.eid_Offset += 1
            else:
                print(
                    """The maximum eid_offset of DiskGroup is reached.
                    The eid of new DiskGroup will not be increased automatically."""
                )
        super(DiskGroup, self).__init__(rangeGroups, propertyDict, eid, util)
        self.n_Disks = n_Disks
        self.disk_Diameter = disk_Diameter
        self.tipWidth = tipWidth
        self.model_Area = model_Area

    def __repr__(self):
        return 'D ' + str(self.disk_Diameter) + ' cutter disk'

    @property
    def disk_Radius(self):
        return self.disk_Diameter / 2

    @property
    def penetration(self):
        return self.util.penetration

    @property
    def actual_Area(self):
        return self.tipWidth * math.sqrt(self.disk_Radius ** 2 - (self.disk_Radius - self.penetration) ** 2)

    @property
    def area_Ratio(self):
        return self.actual_Area / self.model_Area

    @property
    def cc(self):
        return math.tan(math.acos((self.disk_Radius - self.penetration) / self.disk_Radius) / 2)

    def applyDisk_Group(self, y_Coord):
        # it.command(
        #     'structure liner create by-face id ' + str(self.eid) \
        #     + ' group "__Disk_' + str(self.eid) + '__" slot "__TBMUtil__" range group ' \
        #     + generateGroupRangePhrase(self.rangeGroups) + ' position-y ' \
        #     + str(y_Coord - 100 * gc.param['geom_tol']) + ' ' + str(y_Coord + 100 * gc.param['geom_tol'])
        # )
        # it.command(
        #     'structure liner property ' + generatePropertyPhrase(self.propertyDict) \
        #     + ' range id ' + str(self.eid) + ' group "__Disk_' + str(self.eid) + '__" position-y ' \
        #     + str(y_Coord - 100 * gc.param['geom_tol']) + ' ' + str(y_Coord + 100 * gc.param['geom_tol'])
        # )
        it.command(
            'structure liner create by-face id {id} group {sourceGroup} slot {sourceSlot} range group {groupPhrase} {rangePhrase}'.format(
                id=self.eid,
                sourceGroup='"__Disk_{id}__"'.format(id=self.eid),
                sourceSlot='"__TBMUtil__"',
                groupPhrase=generateGroupRangePhrase(self.rangeGroups),
                rangePhrase=generateRangePhrase(ypos=y_Coord)
            )
        )
        it.command(
            'structure liner property {propertyPhrase} range group {groupPhrase} {rangePhrase}'.format(
                propertyPhrase=generatePropertyPhrase(self.propertyDict),
                groupPhrase='"__Disk_{id}__"'.format(id=self.eid),
                rangePhrase=generateRangePhrase(
                    ypos=y_Coord,
                    id=self.eid
                )
            )
        )