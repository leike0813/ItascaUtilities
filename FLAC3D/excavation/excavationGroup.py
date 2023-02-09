# -*- coding: utf-8 -*-
import numpy as np
from ..customDecorators import *
from ..customFunctions import generateRangePhrase
from ..model.abstractSubUtility import AbstractSubUtility
from .. import globalContainer as gc


__all__ = ['ExcaGroup']


class ExcaGroup(AbstractSubUtility):
    """
    ExcaGroup是管理开挖动作的单元，与一个MaterialSlot关联以实现在一个开挖步中根据MaterialSlot指定的单元-材料映射关系更改本构及参数。
    与采用MaterialSlot直接赋参不同，ExcaGroup可对MaterialSlot中的部分group进行操作（采用SubSlot方法），并可根据y坐标分段。
    因此，多个ExcaGroup可共用一个MaterialSlot。
    """
    @convert_Group_To_GroupList
    def __init__(self, y_Bound_Global, groupName_or_List, slotName, util, _assignModel = True):
        super(ExcaGroup, self).__init__(util.modelUtil)
        self.__util = util
        self.groupList = groupName_or_List
        self.slotName = slotName
        self._assignModel = _assignModel
        self.set_y_Bound_Global(y_Bound_Global)

    @property
    def util(self):
        return self.__util

    @y_Bound_Detect('y_Bound_Global')
    def set_y_Bound_Global(self, y_Bound_Global):
        self.y_Bound_Global = y_Bound_Global

    @property
    def subSlot(self):
        return self.modelUtil.zoneUtil.materialSlots[self.slotName].getSubSlot(self.groupList)

    @y_Bound_Detect('y_Bound')
    def exca_Coord(self, y_Bound):
        y_Bound = np.clip(y_Bound, self.y_Bound_Global[0], self.y_Bound_Global[1])
        # self.subSlot.assignMaterials(
        #     'position-y ' + str(y_Bound[0] - gc.param['geom_tol']) + ' ' + str(y_Bound[1] + gc.param['geom_tol']),
        #     self._assignModel
        # )
        self.subSlot.assignMaterials(
            generateRangePhrase(ypos=y_Bound),
            self._assignModel
        )

    @n_Step_Detect
    def exca_Step(self, n_Step):
        y_Bound = np.clip(self.modelUtil.excaUtil.y_BoundList[n_Step], self.y_Bound_Global[0], self.y_Bound_Global[1])
        self.exca_Coord(y_Bound)

    def exca_Step_Periodically_Wrapper(self, period, step_Range, period_Offset = 0):
        """
        周期性开挖函数生成器。
        生成自period_Offset起，每隔period步执行一次长度为step_Range步数的开挖动作的函数。
        返回函数与exca_Step具有同样的输入参数格式。
        """
        def exca_Step_Periodically(n_Step):
            if (n_Step - period_Offset) % period == 0:
                y_Bound = np.array(
                    [self.modelUtil.excaUtil.y_BoundList[n_Step][0],
                     self.modelUtil.excaUtil.y_BoundList[n_Step + step_Range - 1][1]]
                )
                y_Bound = np.clip(y_Bound, self.y_Bound_Global[0], self.y_Bound_Global[1])
                self.exca_Coord(y_Bound)
        return exca_Step_Periodically