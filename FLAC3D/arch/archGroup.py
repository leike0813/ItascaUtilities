# -*- coding: utf-8 -*-
import itasca as it
import numpy as np
import math
from ..customFunctions import generateRangePhrase, generateFixityPhrase
from ..model.abstractGroup import AbstractGroup, AbstractGroup_Instance
from .. import globalContainer as gc


__all__ = ['ArchGroup', 'ArchGroup_Direct']


class ArchGroup_Abstract(AbstractGroup):
    """ArchGroup抽象基类"""
    def __init__(self, ring):
        super(ArchGroup_Abstract, self).__init__(ring.eid, ring, ArchGroup_Instance)
        self.instantiate_Param_List = ['eid']

    def applyArch_Group(self, y_Coord):
        """
        20220325:*由于ArchGroup之间需要连接，故拱架的施加由ArchRing统一调度，此函数几乎不会被调用，保留以备用。
                  考虑多段钢架可能并非同时施加，且分段施加的钢架间需进行连接，ArchGroup的施加逻辑还需进一步细化。
        """
        for i in range(self.n_Line):
            self.util.applyArch_ByLine(
                [self.nodeCoord[i][0], y_Coord, self.nodeCoord[i][1]],
                [self.nodeCoord[i + 1][0], y_Coord, self.nodeCoord[i + 1][1]],
                self.ring.n_Seg,
                self.ring.eid
            )

    def fixNodes_X_Symmetry(self, y_Coord):
        """
        20220325:*由于ArchGroup之间需要连接，故拱架的施加由ArchRing统一调度，此函数几乎不会被调用，保留以备用。
        """
        it.command(
            'structure node fix {fixityPhrase} range {rangePhrase}'.format(
                fixityPhrase=generateFixityPhrase(mode='X_Symm_Node'),
                rangePhrase=generateRangePhrase(xpos=0, ypos=y_Coord, id=self.ring.eid)
            )
        )


class ArchGroup(ArchGroup_Abstract):
    """
    ArchGroup是拱架管理的基本单位，代表一环拱架中的一段。
    ArchGroup的参数有角度范围（angle_Bound）、原点（origin）、半径（radius）和分段数（n_Line）。
    """
    def __init__(self, angle_Bound, n_Line, origin, radius, ring):
        super(ArchGroup, self).__init__(ring)
        self.__angle_Bound = angle_Bound
        self.__origin = origin
        self.__radius = radius
        self.__n_Line = n_Line
        self.calculateNodeCoord()

    def registerInstance(self, instance):
        _paramDict = {
            'type': 'normal',
            'archRing': self.ring,
            'nodeCoord': self.nodeCoord,
            'angle_Bound': self.angle_Bound,
            'origin': self.origin,
            'radius': self.radius,
            'n_Line': self.n_Line,
            'angle_Spacing': self.angle_Spacing
        }
        instance.update_Param(_paramDict)

    @property
    def angle_Bound(self):
        return self.__angle_Bound

    @angle_Bound.setter
    def angle_Bound(self, value):
        self.__angle_Bound = value
        self.calculateNodeCoord()

    @property
    def origin(self):
        return self.__origin

    @origin.setter
    def origin(self, value):
        self.__origin = value
        self.calculateNodeCoord()

    @property
    def radius(self):
        return self.__radius

    @radius.setter
    def radius(self, value):
        self.__radius = value
        self.calculateNodeCoord()

    @property
    def n_Line(self):
        return self.__n_Line

    @n_Line.setter
    def n_Line(self, value):
        self.__n_Line = value
        self.calculateNodeCoord()

    @property
    def angle_Spacing(self):
        return self.__angle_Spacing

    def calculateNodeCoord(self):
        # 计算角度间隔
        self.__angle_Spacing = (self.angle_Bound[1] - self.angle_Bound[0]) / self.n_Line
        # 计算xOz平面上的节点坐标
        self.setNodeCoord(np.array(
            [
                (
                    self.origin[0] + self.radius * math.sin(math.radians(self.angle_Bound[0] + i * self.angle_Spacing)),
                    self.origin[1] + self.radius * math.cos(math.radians(self.angle_Bound[0] + i * self.angle_Spacing))
                ) for i in range(self.n_Line + 1)
            ]
        ))

    def applyArch_Group(self, y_Coord):
        """
        20220325:*由于ArchGroup之间需要连接，故拱架的施加由ArchRing统一调度，此函数几乎不会被调用，保留以备用。
        """
        super(ArchGroup, self).applyArch_Group(y_Coord)
        if self.modelUtil.modelType == gc.ModelType.half_Model and \
                (min(self.angle_Bound) <= 0 or max(self.angle_Bound) >= 180):
            # 若模型为对称模型，且该ArchGroup的边界与对称面相交，则施加对称约束
            # it.command(
            #     'structure node fix velocity-x rotation-y rotation-z range position-x 0 position-y ' \
            #     + str(y_Coord - gc.param['geom_tol']) + ' ' + str(y_Coord + gc.param['geom_tol']) + ' id ' + str(self.ring.eid)
            # )
            # it.command(
            #     'structure node fix {fixityPhrase} range {rangePhrase}'.format(
            #         fixityPhrase=generateFixityPhrase(mode='X_Symm_Node'),
            #         rangePhrase=generateRangePhrase(xpos=0, ypos=y_Coord, id=self.ring.eid)
            #     )
            # )
            super(ArchGroup, self).fixNodes_X_Symmetry(y_Coord)


class ArchGroup_Direct(ArchGroup_Abstract):
    """
    直接赋予拱架节点坐标的ArchGroup。
    参数有节点坐标（nodeCoord）和对称性标志（_symmetry）。
    节点坐标（nodeCoord）必须是以浮点数（整数）为元素的二维可索引对象，其中第1维索引代表一个拱架节点，第2维索引为坐标分量（x、z）。
    当对称性标志（_symmetry）为True时，添加锚杆后自动在x=0平面施加对称约束。
    """

    def __init__(self, nodeCoord, _symmetry, ring):
        super(ArchGroup_Direct, self).__init__(ring)
        self.setNodeCoord(nodeCoord)
        self._symmetry = _symmetry and self.modelUtil.modelType == gc.ModelType.full_Model  # _symmety标志仅在全模型时生效
        self.instantiate_Param_List.append('_symmetry')

    def registerInstance(self, instance):
        _paramDict = {
            'type': 'direct',
            'archRing': self.ring,
            'nodeCoord': self.nodeCoord,
            'n_Line': self.n_Line
        }
        instance.update_Param(_paramDict)

    @property
    def n_Line(self):
        return len(self.nodeCoord)

    def getArchGPCoordAndSort(self, groupName1, groupName2):
        """
        20220325:*复制自ArchRing_Direct，优化后该函数应位于ArchGroup_Direct下，原函数保留以保证向后兼容。
        根据输入的两个group名，自动计算其边界上的节点坐标并排序后作为拱架的施加坐标。
        输入的两个group一般为开挖边界两侧的group。
        """
        # yMask为y坐标小于等于0的节点的蒙版数组。
        # 默认模型y轴正向为隧道开挖方向，且y轴负向边界为y=0，故yMask代表模型边界面上的所有节点。
        yMask = self.modelUtil.gpUtil.pos_y < gc.param['geom_tol']
        # gpArray为两个group所包含节点的交集。
        gpArray = self.modelUtil.zoneUtil.gridPoints_Group_Intersect([groupName1, groupName2])
        # gpMask为对应于gpArray的蒙版数组。
        gpMask = np.array([True if i in gpArray else False for i in range(it.gridpoint.count())])
        # 求gpMask和yMask的交集。
        gpMask_y = np.logical_and(gpMask, yMask)
        if self.modelUtil.modelType == gc.ModelType.half_Model:
            # 若模型为半模型，直接取得节点坐标数组
            archGPCoord = self.modelUtil.gpUtil.pos[gpMask_y]
        else:
            if self._symmetry:
                # 若模型为全模型且_symmetry标志为True，则用x>=0的蒙版数组求交集后取得节点坐标数组。
                xMask = self.modelUtil.gpUtil.pos_x >= -gc.param['geom_tol']
                archGPCoord = self.modelUtil.gpUtil.pos[np.logical_and(gpMask_y, xMask)]
            else:
                # 若模型为全模型且_symmetry标志为False，则分别取出x>=0和x<0的节点坐标数组。
                xMask_Pos = self.modelUtil.gpUtil.pos_x >= -gc.param['geom_tol']
                xMask_Neg = self.modelUtil.gpUtil.pos_x < -gc.param['geom_tol']
                # 删除y坐标，得到(x,z)坐标的二元组。
                archGPCoord_Pos = np.delete(
                    self.modelUtil.gpUtil.pos[np.logical_and(gpMask_y, xMask_Pos)],
                    1,
                    axis=1
                )
                archGPCoord_Neg = np.delete(
                    self.modelUtil.gpUtil.pos[np.logical_and(gpMask_y, xMask_Neg)],
                    1,
                    axis=1
                )
                # 对于x>=0部分，按z坐标升序排列；对于x<0部分，按z坐标降序排列，保证单元施加顺序为逆时针（沿y轴正向看去）
                archGPCoord_Pos = archGPCoord_Pos[np.argsort(archGPCoord_Pos[:, 1])]
                archGPCoord_Neg = archGPCoord_Neg[np.argsort(-archGPCoord_Neg[:, 1])]
                # 若排序后的x>=0部分的第一个节点为x=0，说明该ArchGroup在下方首尾相接，需要在合并后的节点坐标数组末端再添加一次第一个节点。
                # 反之则不需要
                if abs(archGPCoord_Pos[0, 0]) < gc.param['geom_tol']:
                    self.__nodeCoord = np.vstack((archGPCoord_Pos, archGPCoord_Neg, archGPCoord_Pos[0, :]))
                else:
                    self.__nodeCoord = np.vstack((archGPCoord_Pos, archGPCoord_Neg))
                return
        # 对应于半模型或全模型+_symmetry标志开的情况
        # 删除y坐标
        archGPCoord = np.delete(archGPCoord, 1, axis=1)
        # 排序
        self.setNodeCoord(archGPCoord[np.argsort(archGPCoord[:, 1])])

    def applyArch_Group(self, y_Coord):
        """
        20220325:*由于ArchGroup之间需要连接，故拱架的施加由ArchRing统一调度，此函数几乎不会被调用，保留以备用。
        """
        super(ArchGroup_Direct, self).applyArch_Group(y_Coord)
        if self.modelUtil.modelType == gc.ModelType.half_Model:
            # 若模型为对称模型，则施加对称约束
            super(ArchGroup_Direct, self).fixNodes_X_Symmetry(y_Coord)


class ArchGroup_Instance(AbstractGroup_Instance):
    def __init__(self, y_Coord, parent, generator, manager):
        super(ArchGroup_Instance, self).__init__(y_Coord, parent, generator, manager)

    def __repr__(self):
        return 'Arch group instance at Y={y_Coord}'.format(y_Coord=self.y_Coord)
