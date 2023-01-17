# -*- coding: utf-8 -*-
import itasca as it
import numpy as np
from ..customDecorators import *
from ..customFunctions import generatePropertyPhrase, generateRangePhrase, generateFixityPhrase
from archGroup import *
from .. import globalContainer as gc


__all__ = ['ArchRing', 'ArchRing_Direct']

class ArchRing_Abstract(object):
    """
    ArchRing抽象基类，避免重复代码。

    20220327：已优化代码，ArchRing抽象基类仅作为弃用的ArchRing_Direct父类予以暂时保留以向后兼容。所有代码已整合至新的ArchRing类。
    """
    base_ID = gc.param['id_base_offset'] + 30
    id_Offset = 1

    @classmethod
    def current_ID(cls):
        return cls.base_ID + cls.id_Offset

    def __init__(self, y_Bound_Global, spacing, n_Seg, propertyDict, _id, archUtil):
        if _id == 'default':
            _id = ArchRing_Abstract.current_ID()
            if ArchRing_Abstract.id_Offset < 19:
                ArchRing_Abstract.id_Offset += 1
            else:
                print(
                    """The maximum id_offset of ArchRing is reached.
                    The id of new ArchRing will not be increased automatically."""
                )
        self.archUtil = archUtil
        self.modelUtil = archUtil.modelUtil
        self.spacing = spacing
        self.n_Seg = n_Seg
        self._id = _id
        self.propertyDict = propertyDict
        self.set_y_Bound_Global(y_Bound_Global)

    @y_Bound_Detect('y_Bound_Global')
    def set_y_Bound_Global(self, y_Bound_Global):
        '''设置该ArchRing在模型中的y坐标范围'''
        self.y_Bound_Global = y_Bound_Global

    def applyArch_Ring(self, y_, _assignProp = False):
        """
        在y坐标为y_的位置施加一环ArchRing
        """
        for i in range(self.nodeCoord.shape[0] - 1):
            self.archUtil.applyArch_ByLine(
                [self.nodeCoord[i, 0], y_, self.nodeCoord[i, 1]],
                [self.nodeCoord[i + 1, 0], y_, self.nodeCoord[i + 1, 1]],
                self.n_Seg,
                self._id
            )
        if np.any(abs(self.modelUtil.gpUtil.bounding_y - y_) < gc.param['geom_tol']):
            # 若输入的y坐标为模型的y向边界，则施加y向对称约束
            # it.command(
            #     'structure node fix velocity-y rotation-x rotation-z range position-y ' \
            #     + str(y_ - gc.param['geom_tol']) + ' ' + str(y_ + gc.param['geom_tol']) \
            #     + ' id ' + str(self._id)
            # )
            it.command(
                'structure node fix {fixityPhrase} range {rangePhrase}'.format(
                    fixityPhrase=generateFixityPhrase(mode='Y_Symm_Node'),
                    rangePhrase=generateRangePhrase(ypos=y_, id=self._id)
                )
            )
        if _assignProp:
            # 若_assignProp标志为True，则在施加单元后赋予参数
            # it.command(
            #     'structure beam property ' + generatePropertyPhrase(self.propertyDict) + ' range position-y ' \
            #     + str(y_ - gc.param['geom_tol']) + ' ' + str(y_ + gc.param['geom_tol']) + ' id ' + str(self._id)
            # )
            it.command(
                'structure beam property {propertyPhrase} range {rangePhrase}'.format(
                    propertyPhrase=generatePropertyPhrase(self.propertyDict),
                    rangePhrase=generateRangePhrase(ypos=y_, id=self._id)
                )
            )

    def applyArch_Coord_Ring(self, y_Bound):
        """
        在y_Bound给定的y坐标范围内，根据ArchRing的spacing自动计算需要施加ArchRing的位置
        """
        # 若输入的y坐标范围超出模型边界，则对其进行限制
        y_Bound = np.clip(y_Bound, self.y_Bound_Global[0], self.y_Bound_Global[1])
        # 计算在y坐标范围内的环数
        cross_Range = np.array([
            int((y_Bound[0] - gc.param['geom_tol'] - self.y_Bound_Global[0]) // self.spacing),
            int((y_Bound[1] - gc.param['geom_tol'] - self.y_Bound_Global[0]) // self.spacing)
        ])
        n_Cross = cross_Range[1] - cross_Range[0]
        # 逐环调用applyArch_Ring方法施加单元
        for i in range(n_Cross):
            self.applyArch_Ring((cross_Range[1] - i) * self.spacing + self.y_Bound_Global[0])
        if n_Cross > 0:
            # 若成功施加了一环以上的单元，则赋予参数
            # it.command(
            #     'structure beam property ' + generatePropertyPhrase(self.propertyDict) + ' range position-y ' \
            #     + str(y_Bound[0] - gc.param['geom_tol']) + ' ' + str(y_Bound[1] + gc.param['geom_tol']) + ' id ' + str(self._id)
            # )
            it.command(
                'structure beam property {propertyPhrase} range {rangePhrase}'.format(
                    propertyPhrase=generatePropertyPhrase(self.propertyDict),
                    rangePhrase=generateRangePhrase(ypos=y_Bound, id=self._id)
                )
            )


class ArchRing_Direct(ArchRing_Abstract):
    """
    直接赋予全环拱架节点坐标的ArchRing，不包含ArchGroup。
    参数有拱架节点坐标（nodeCoord）、纵向坐标范围（y_Bound_Global）、间距（spacing）、单元划分数（n_Seg）、ID（_id)和参数（propertyDict）。
    节点坐标（nodeCoord）必须是以浮点数（整数）为元素的二维可索引对象，其中第1维索引代表一个拱架节点，第2维索引为坐标分量（x、z）。

    20220325：*存在进一步优化的可能，Ring级容器不分Direct与否，全部交由Group级容器管理。前台业务代码需相应改变。
    20220327：*已根据前一条issue优化代码，ArchRing_Direct保留，以满足代码向后兼容。getArchGPCoordAndSort函数整合入ArchGroup_Direct。
    """
    def __init__(self, y_Bound_Global, spacing, n_Seg, propertyDict, nodeCoord, _symmetry, _id, archUtil):
        super(ArchRing_Direct, self).__init__(y_Bound_Global, spacing, n_Seg, propertyDict, _id, archUtil)
        self.nodeCoord = nodeCoord
        self._symmetry = _symmetry and self.modelUtil.modelType == gc.ModelType.full_Model #_symmety标志仅在全模型时生效

    def getArchGPCoordAndSort(self, groupName1, groupName2):
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
                    axis = 1
                )
                archGPCoord_Neg = np.delete(
                    self.modelUtil.gpUtil.pos[np.logical_and(gpMask_y, xMask_Neg)],
                    1,
                    axis = 1
                )
                # 对于x>=0部分，按z坐标升序排列；对于x<0部分，按z坐标降序排列，保证单元施加顺序为逆时针（沿y轴正向看去）
                archGPCoord_Pos = archGPCoord_Pos[np.argsort(archGPCoord_Pos[:, 1])]
                archGPCoord_Neg = archGPCoord_Neg[np.argsort(-archGPCoord_Neg[:, 1])]
                # 若排序后的x>=0部分的第一个节点为x=0，说明该ArchGroup在下方首尾相接，需要在合并后的节点坐标数组末端再添加一次第一个节点。
                # 反之则不需要
                if abs(archGPCoord_Pos[0, 0]) < gc.param['geom_tol']:
                    self.nodeCoord = np.vstack((archGPCoord_Pos, archGPCoord_Neg, archGPCoord_Pos[0, :]))
                else:
                    self.nodeCoord = np.vstack((archGPCoord_Pos, archGPCoord_Neg))
                return
        # 对应于半模型或全模型+_symmetry标志开的情况
        # 删除y坐标
        archGPCoord = np.delete(archGPCoord, 1, axis = 1)
        # 排序
        self.nodeCoord = archGPCoord[np.argsort(archGPCoord[:, 1])]

    def applyArch_Coord_Ring(self, y_Bound):
        super(ArchRing_Direct, self).applyArch_Coord_Ring(y_Bound)
        if self.modelUtil.modelType == gc.ModelType.half_Model:
            # 若模型为对称模型，则施加对称约束
            # it.command(
            #     'structure node fix velocity-x rotation-y rotation-z range position-x 0 position-y ' \
            #     + str(y_Bound[0] - gc.param['geom_tol']) + ' ' + str(y_Bound[1] + gc.param['geom_tol']) + ' id ' + str(self._id)
            # )
            it.command(
                'structure node fix {fixityPhrase} range {rangePhrase}'.format(
                    fixityPhrase=generateFixityPhrase(mode='X_Symm_Node'),
                    rangePhrase=generateRangePhrase(xpos=0, ypos=y_Bound, id=self._id)
                )
            )


class ArchRing(ArchRing_Abstract):
    """
    ArchRing是钢架管理的第二级容器，代表“一环”钢架。
    ArchRing的参数有纵向坐标范围（y_Bound_Global）、间距（spacing）、单元划分数（n_Seg）、ID（_id)和参数（propertyDict）。
    每个ArchRing包含若干个ArchGroup。

    20220327：*已优化代码，ArchRing现在不再继承自ArchRing_Abstract抽象基类，抽象基类中代码已整合入内。
    20230115：*回滚上一条改动，ArchRing仍继承ArchRing_Abstract抽象基类
    """
    def __init__(self, y_Bound_Global, spacing, n_Seg, propertyDict, _id, archUtil):
        super(ArchRing, self).__init__(y_Bound_Global, spacing, n_Seg, propertyDict, _id, archUtil)
        self.nodeCoord = None
        self.__archGroupList = []

    @property
    def n_ArchGroup(self):
        return len(self.__archGroupList)

    @property
    def archGroups(self):
        return self.__archGroupList

    def calculateNodeCoord(self):
        """
        根据各ArchGroup的信息计算并整合为ArchRing的节点坐标数组，以便统一调度施加单元
        """
        if self.n_ArchGroup >= 1:
            # 若仅包含一个ArchGroup，则直接采用该ArchGroup的节点坐标数组
            _nodeCoord = self.archGroups[0].nodeCoord[:]
            for i in range(1, self.n_ArchGroup):
                # 若包含大于1个ArchGroup，则进行遍历
                if (
                        (self.archGroups[i].nodeCoord[0][0] - _nodeCoord[-1][0]) ** 2
                        + (self.archGroups[i].nodeCoord[0][1] - _nodeCoord[-1][1]) ** 2
                ) <= gc.param['geom_tol'] ** 2:
                    # 若上一个ArchGroup最后一个节点的坐标与下一个ArchGroup第一个节点坐标相同，则从第二个节点开始拼接，否则从第一个开始
                    _nodeCoord = np.vstack((_nodeCoord, self.archGroups[i].nodeCoord[1:]))
                else:
                    _nodeCoord = np.vstack((_nodeCoord, self.archGroups[i].nodeCoord[:]))
            self.nodeCoord = _nodeCoord

    def newArchGroup(self, angle_Bound, n_Line, origin, radius):
        """
        增加新的ArchGroup
        """
        archGroup = ArchGroup(angle_Bound, n_Line, origin, radius, self)
        self.__archGroupList.append(archGroup)
        self.calculateNodeCoord()
        return archGroup

    def newArchGroup_Direct(self, nodeCoord = None, _symmetry = False):
        """
        增加新的ArchGroup_Direct
        默认nodeCoord为None，若如此，则需要调用ArchGroup_Direct中的getArchGPCoordAndSort计算nodeCoord
        """
        archGroup = ArchGroup_Direct(nodeCoord, _symmetry, self)
        self.__archGroupList.append(archGroup)
        if nodeCoord:
            self.calculateNodeCoord()
        return archGroup