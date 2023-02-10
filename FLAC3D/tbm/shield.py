# -*- coding: utf-8 -*-
import itasca as it
from vec import vec3
from ..customDecorators import *
from ..customFunctions import *
from abstractTBMComponent import AbstractTBMComponent
from .. import globalContainer as gc


__all__ = ['Shield']

class Shield(AbstractTBMComponent):
    base_eid = gc.param['eid_base_offset'] + 99
    def __init__(self, rangeGroups, origin, diameter, lengthCoef, preserveDisp, frictionCoef, propertyDict, eid, util):
        if eid == 'default':
            eid = Shield.base_eid
        super(Shield, self).__init__(rangeGroups, propertyDict, eid, util)
        self.lengthCoef = lengthCoef
        self.preserveDisp = preserveDisp
        self.frictionCoef = frictionCoef
        self.__origin = origin
        self.__diameter = diameter
        self.excaBoundGridpoints = None
        if self.preserveDisp > 0:
            self.getExcaBoundGridpoints(rangeGroups, self.origin, self.diameter)
            it.set_callback('_update_ShieldLink', -1)

    def __repr__(self):
        return 'D ' + str(self.diameter) + ' shield'

    def __getstate__(self):
        state = self.__dict__.copy()
        Shield.saveExcaBoundGridpoints(state)
        # state.pop('excaBoundGridpoints')
        return state

    def __setstate__(self, state):
        Shield.restoreExcaBoundGridpoints(state)
        self.__dict__.update(state)
        # self.excaBoundGridpoints = None
        # if self.preserveDisp > 0:
        #     self.getExcaBoundGridpoints(self.rangeGroups, self.origin, self.diameter)

    @property
    def origin(self):
        return self.util.origin if self.__origin == None else self.__origin

    @property
    def diameter(self):
        return self.util.diameter if self.__diameter == None else self.__diameter

    @property
    def radius(self):
        return self.diameter / 2

    @convert_Group_To_GroupList
    def getExcaBoundGridpoints(self, groupName_or_List, origin, diameter):
        self.excaBoundGridpoints = [[] for i in range(self.modelUtil.excaUtil.n_ExcaStep)]
        for gp in it.gridpoint.list():
            for gr in groupName_or_List:
                if gp.in_group(gr, 'any'):
                    for i in range(self.modelUtil.excaUtil.n_ExcaStep):
                        if (
                                (gp.pos_y() < self.modelUtil.excaUtil.y_BoundList[i][1 ]+ gc.param['geom_tol'])
                                and (gp.pos_y() > self.modelUtil.excaUtil.y_BoundList[i][0] - gc.param['geom_tol'])
                                and (
                                abs(
                                    (gp.pos_x() - origin[0]) ** 2 + (gp.pos_z() - origin[1]) ** 2 - diameter ** 2 / 4.0
                                ) < gc.param['geom_tol']
                            )
                        ):
                            self.excaBoundGridpoints[i].append(gp)
                            gp.set_extra(1, gp.disp())

    @staticmethod
    def saveExcaBoundGridpoints(state):
        state['excaBoundGridpoints_ID'] = []
        for _group in state['excaBoundGridpoints']:
            state['excaBoundGridpoints_ID'].append([gp.id() for gp in _group])
        state.pop('excaBoundGridpoints')

    @staticmethod
    def restoreExcaBoundGridpoints(state):
        state['excaBoundGridpoints'] = []
        for _group in state['excaBoundGridpoints_ID']:
            state['excaBoundGridpoints'].append([it.gridpoint.find(id) for id in _group])
        state.pop('excaBoundGridpoints_ID')

    @y_Bound_Detect('y_Bound')
    def applyShield_Coord(self, y_Bound):
        # it.command(
        #     'structure liner create by-face id ' + str(self.eid) \
        #     + ' group "__Shield__" slot "__TBMUtil__" range group ' \
        #     + generateGroupRangePhrase(self.rangeGroups) + ' cylinder end-1 ' \
        #     + str(self.origin[0]) + ' ' + str(y_Bound[0] - 100 * gc.param['geom_tol'])\
        #     + ' ' + str(self.origin[1]) + ' end-2 ' + str(self.origin[0])\
        #     + ' ' + str(y_Bound[1] + 100 * gc.param['geom_tol']) + ' ' + str(self.origin[1])\
        #     + ' radius ' + str(self.radius)
        # )
        it.command(
            'structure liner create by-face id {id} group {sourceGroup} slot {sourceSlot} range group {groupPhrase} {rangePhrase}'.format(
                id=self.eid,
                sourceGroup='"__Shield__"',
                sourceSlot='"__TBMUtil__"',
                groupPhrase=generateGroupRangePhrase(self.rangeGroups),
                rangePhrase=generateRangePhrase(cyl=(
                    (self.origin[0], y_Bound[0] - gc.param['geom_tol'], self.origin[1]),
                    (self.origin[0], y_Bound[1] + gc.param['geom_tol'], self.origin[1]),
                    self.radius
                ))
            )
        )
        # it.command(
        #     'structure liner property ' + generatePropertyPhrase(self.propertyDict) \
        #     + ' range id ' + str(self.eid) + ' group "__Shield__" position-y ' \
        #     + str(y_Bound[0] - 100 * gc.param['geom_tol']) + ' ' + str(y_Bound[1] + 100 * gc.param['geom_tol'])
        # )
        it.command(
            'structure liner property {propertyPhrase} range group {groupPhrase} {rangePhrase}'.format(
                propertyPhrase=generatePropertyPhrase(self.propertyDict),
                groupPhrase='"__Shield__"',
                rangePhrase=generateRangePhrase(
                    ypos=y_Bound,
                    id=self.eid
                )
            )
        )
        if self.preserveDisp > 0:
            # it.command(
            #     'structure link delete range id ' + str(self.eid) + ' group "__Shield__" position-y ' \
            #     + str(y_Bound[0] - 100 * gc.param['geom_tol']) + ' ' + str(y_Bound[1] + 100 * gc.param['geom_tol'])
            # )
            it.command(
                'structure link delete range group {groupPhrase} {rangePhrase}'.format(
                    groupPhrase='"__Shield__"',
                    rangePhrase=generateRangePhrase(
                        ypos=y_Bound,
                        id=self.eid
                    )
                )
            )
        if self.modelUtil.modelType == gc.ModelType.half_Model:
            # it.command(
            #     'structure node fix velocity-x rotation-y rotation-z range id ' + str(self.eid) \
            #     + ' group "__Shield__" position-x 0 position-y ' \
            #     + str(y_Bound[0] - 100 * gc.param['geom_tol']) + ' ' + str(y_Bound[1] + 100 * gc.param['geom_tol'])
            # )
            it.command(
                'structure node fix {fixityPhrase} range group {groupPhrase} {rangePhrase}'.format(
                    fixityPhrase=generateFixityPhrase(mode='X_Symm_Node'),
                    groupPhrase='"__Shield__"',
                    rangePhrase=generateRangePhrase(
                        xpos=0,
                        ypos=y_Bound,
                        id=self.eid
                    )
                )
            )

    @y_Bound_Detect('y_Bound')
    def removeShield_Coord(self, y_Bound):
        # it.command(
        #     'structure liner delete range id ' + str(self.eid) \
        #     + ' group "__Shield__" position-y ' \
        #     + str(y_Bound[0] - 100 * gc.param['geom_tol']) + ' ' + str(y_Bound[1] + 100 * gc.param['geom_tol'])
        # )
        it.command(
            'structure liner delete range group {groupPhrase} {rangePhrase}'.format(
                groupPhrase='"__Shield__"',
                rangePhrase=generateRangePhrase(
                    ypos=y_Bound,
                    id=self.eid
                )
            )
        )

    @n_Step_Detect
    def freezeExcaBoundDisp_Step(self, n_Step):
        if self.preserveDisp > 0:
            for gp in self.excaBoundGridpoints[n_Step]:
                gp.set_extra(1, gp.disp())

    @n_Step_Detect
    def updateShieldLink_Step(self, n_Step, _force = False):
        if it.cycle() % 10 == 0 or _force:
            for gp in self.excaBoundGridpoints[n_Step]:
                gp_XPos_Gen = gp.pos_x() + gp.disp_x() - gp.extra(1)[0]
                gp_ZPos_Gen = gp.pos_z() + gp.disp_z() - gp.extra(1)[2]
                if (gp_XPos_Gen - self.origin[0]) ** 2 \
                        + (gp_ZPos_Gen - self.origin[1] + self.preserveDisp / 2) ** 2 \
                        <= (self.radius - self.preserveDisp / 2) ** 2:
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