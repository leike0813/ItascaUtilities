# -*- coding: utf-8 -*-
import itasca as it
from vec import vec3
import math
from ..customDecorators import *
from ..customFunctions import *
from abstractTBMComponent import AbstractTBMComponent
from .. import globalContainer as gc


__all__ = ['CutterHead']

class CutterHead(AbstractTBMComponent):
    base_ID = gc.param['id_base_offset'] + 98
    def __init__(self, groupList, origin, diameter, cutterHeight, frictionCoef, propertyDict, _id, tbmUtil):
        if _id == 'default':
            _id = CutterHead.base_ID
        super(CutterHead, self).__init__(groupList, propertyDict, _id, tbmUtil)
        self.cutterHeight = cutterHeight
        self.frictionCoef = frictionCoef
        self.__origin = origin
        self.__diameter = diameter
        self.excaFaceGridpoints = None
        if self.cutterHeight > 0:
            self.getExcaFaceGridpoints(groupList)
            it.set_callback('_update_CutterHeadLink', -1)

    def __repr__(self):
        return 'D ' + str(self.diameter) + ' cutter head'

    def __getstate__(self):
        state = self.__dict__.copy()
        CutterHead.saveExcaFaceGridpoints(state)
        # state.pop('excaFaceGridpoints')
        return state

    def __setstate__(self, state):
        CutterHead.restoreExcaFaceGridpoints(state)
        self.__dict__.update(state)
        # self.excaFaceGridpoints = None
        # if self.cutterHeight > 0:
        #     self.getExcaFaceGridpoints(self.groupList)

    @property
    def origin(self):
        return self.tbmUtil.origin if self.__origin == None else self.__origin

    @property
    def diameter(self):
        return self.tbmUtil.diameter if self.__diameter == None else self.__diameter

    @property
    def radius(self):
        return self.diameter / 2

    @property
    def penetration(self):
        return self.tbmUtil.penetration

    @property
    def area(self):
        area_full = math.pi * self.radius ** 2
        return area_full / 2 if self.modelUtil.modelType == gc.ModelType.half_Model else area_full

    @property
    def area_contact(self):
        if self.cutterHeight == 0:
            return self.area
        area_contact_ = 0.0
        for lk in it.structure.link.list():
            if lk.in_group('__CutterHead__'):
                area_contact_ += lk.model_area()[1]
        return area_contact_

    @convert_Group_To_GroupList
    def getExcaFaceGridpoints(self, groupName_or_List):
        self.excaFaceGridpoints = [[] for i in range(self.modelUtil.excaUtil.n_ExcaStep)]
        for gp in it.gridpoint.list():
            for gr in groupName_or_List:
                if gp.in_group(gr, 'any'):
                    for i in range(self.modelUtil.excaUtil.n_ExcaStep):
                        if abs(gp.pos_y() - self.modelUtil.excaUtil.y_BoundList[i][1]) < gc.param['geom_tol']:
                            self.excaFaceGridpoints[i].append(gp)
                            gp.set_extra(1, gp.disp())

    @staticmethod
    def saveExcaFaceGridpoints(state):
        state['excaFaceGridpoints_ID'] = []
        for _group in state['excaFaceGridpoints']:
            state['excaFaceGridpoints_ID'].append([gp.id() for gp in _group])
        state.pop('excaFaceGridpoints')

    @staticmethod
    def restoreExcaFaceGridpoints(state):
        state['excaFaceGridpoints'] = []
        for _group in state['excaFaceGridpoints_ID']:
            state['excaFaceGridpoints'].append([it.gridpoint.find(_id) for _id in _group])
        state.pop('excaFaceGridpoints_ID')

    def applyCutterHead(self, y_):
        # it.command(
        #     'structure liner create by-face id ' + str(self._id) \
        #     + ' group "__CutterHead__" slot "__TBMUtil__" range group ' \
        #     + generateGroupRangePhrase(self.groupList) + ' cylinder end-1 ' \
        #     + str(self.origin[0]) + ' ' + str(y_ - 100 * gc.param['geom_tol'])\
        #     + ' ' + str(self.origin[1]) + ' end-2 ' + str(self.origin[0])\
        #     + ' ' + str(y_ + 100 * gc.param['geom_tol']) + ' ' + str(self.origin[1])\
        #     + ' radius ' + str(self.radius)
        # )
        it.command(
            'structure liner create by-face id {_id} group {sourceGroup} slot {sourceSlot} '.format(
                _id=self._id,
                sourceGroup='"__CutterHead__"',
                sourceSlot='"__TBMUtil__"'
            ) + 'range group {groupPhrase} {rangePhrase}'.format(
                groupPhrase=generateGroupRangePhrase(self.groupList),
                rangePhrase=generateRangePhrase(cyl=(
                    (self.origin[0], y_ - gc.param['geom_tol'], self.origin[1]),
                    (self.origin[0], y_ + gc.param['geom_tol'], self.origin[1]),
                    self.radius
                ))
            )
        )
        # it.command(
        #     'structure liner property ' + generatePropertyPhrase(self.propertyDict) \
        #     + ' range id ' + str(self._id) + ' group "__CutterHead__" position-y ' \
        #     + str(y_ - 100 * gc.param['geom_tol']) + ' ' + str(y_ + 100 * gc.param['geom_tol'])
        # )
        it.command(
            'structure liner property {propertyPhrase} range group {groupPhrase} {rangePhrase}'.format(
                propertyPhrase=generatePropertyPhrase(self.propertyDict),
                groupPhrase='"__CutterHead__"',
                rangePhrase=generateRangePhrase(ypos=y_, id=self._id)
            )
        )
        # it.command(
        #     'structure node fix velocity-x velocity-y velocity-z rotation-x rotation-y rotation-z range id '\
        #     + str(self._id) + ' group "__CutterHead__" cylinder end-1 ' \
        #     + str(self.origin[0]) + ' ' + str(y_ - 100 * gc.param['geom_tol']) + ' ' + str(self.origin[1]) + ' end-2 ' \
        #     + str(self.origin[0]) + ' ' + str(y_ + 100 * gc.param['geom_tol']) + ' ' + str(self.origin[1]) + \
        #     ' radius ' + str(self.radius - 100 * gc.param['geom_tol']) + ' ' + str(self.radius + 100 * gc.param['geom_tol'])
        # )
        it.command(
            'structure node fix {fixityPhrase} range group {groupPhrase} {rangePhrase}'.format(
                fixityPhrase=generateFixityPhrase(mode='Encastre'),
                groupPhrase='"__CutterHead__"',
                rangePhrase=generateRangePhrase(
                    cyl=(
                        (self.origin[0], y_ - gc.param['geom_tol'], self.origin[1]),
                        (self.origin[0], y_ + gc.param['geom_tol'], self.origin[1]),
                        (self.radius, self.radius)
                    ),
                    id=self._id
                )
            )
        )
        if self.cutterHeight > 0:
            # it.command(
            #     'structure link delete range id ' + str(self._id) + ' group "__CutterHead__" position-y ' \
            #     + str(y_ - 100 * gc.param['geom_tol']) + ' ' + str(y_ + 100 * gc.param['geom_tol'])
            # )
            it.command(
                'structure link delete range group {groupPhrase} {rangePhrase}'.format(
                    groupPhrase='"__CutterHead__"',
                    rangePhrase=generateRangePhrase(ypos=y_, id=self._id)
                )
            )
        if self.model.modelType == gc.ModelType.half_Model:
            # it.command(
            #     'structure node fix velocity-x rotation-y rotation-z range id ' + str(self._id) \
            #     + ' group "__CutterHead__" position-x 0 position-y ' \
            #     + str(y_ - 100 * gc.param['geom_tol']) + ' ' + str(y_ + 100 * gc.param['geom_tol'])
            # )
            it.command(
                'structure node fix {fixityPhrase} range group {groupPhrase} {rangePhrase}'.format(
                    fixityPhrase=generateFixityPhrase(mode='X_Symm_Node'),
                    groupPhrase='"__CutterHead__"',
                    rangePhrase=generateRangePhrase(xpos=0, ypos=y_, id=self._id)
                )
            )

    def removeCutterHead(self, y_):
        # it.command(
        #     'structure liner delete range id ' + str(self._id) \
        #     + ' group "__CutterHead__" position-y ' \
        #     + str(y_ - 100 * gc.param['geom_tol']) + ' ' + str(y_ + 100 * gc.param['geom_tol'])
        # )
        it.command(
            'structure liner delete range group {groupPhrase} {rangePhrase}'.format(
                groupPhrase='"__CutterHead__"',
                rangePhrase=generateRangePhrase(ypos=y_, id=self._id)
            )
        )

    @n_Step_Detect
    def freezeExcaFaceDisp_Step(self, n_Step):
        if self.cutterHeight > 0:
            for gp in self.excaFaceGridpoints[n_Step]:
                gp.set_extra(1, gp.disp())

    @n_Step_Detect
    def updateCutterHeadLink_Step(self, n_Step, _force = False):
        if it.cycle() % 10 == 0 or _force:
            for gp in self.excaFaceGridpoints[n_Step]:
                gp_YPos_Gen = gp.pos_y() + gp.disp_y() - gp.extra(1)[1]
                if gp_YPos_Gen <= self.model.excaUtil.y_BoundList[n_Step][1] - self.cutterHeight + self.penetration:
                    gp_Zone_ID = gp.zones()[0].id()
                    gp_Tar_Node = it.structure.node.near(vec3((gp.pos_x(), gp.pos_y(), gp.pos_z())))
                    gp_Tar_Node_ID = gp_Tar_Node.component_id()
                    if gp_Tar_Node.links()[0] is None:
                        # it.command(
                        #     "structure link create default-attach true on-nodeid " \
                        #     + str(gp_Tar_Node_ID) + " target zone " + str(gp_Zone_ID)
                        # )
                        it.command(
                            'structure link create default-attach true on-nodeid {nodeid} target zone {zoneid}'.format(
                                nodeid=gp_Tar_Node_ID,
                                zoneid=gp_Zone_ID
                            )
                        )