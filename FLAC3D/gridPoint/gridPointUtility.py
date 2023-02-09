# -*- coding: utf-8 -*-
import itasca as it
from itasca import gridpointarray as gpa
import numpy as np
from ..model.abstractSubUtility import AbstractSubUtility
from .. import globalContainer as gc


__all__ = ['GridPointUtility']

class GridPointUtility(AbstractSubUtility):
    def __init__(self, model=None):
        super(GridPointUtility, self).__init__(model)

    @property
    def count(self):
        return it.gridpoint.count()

    @property
    def pos(self):
        return gpa.pos()

    @property
    def pos_x(self):
        return gpa.pos().T[0]

    @property
    def pos_y(self):
        return gpa.pos().T[1]

    @property
    def pos_z(self):
        return gpa.pos().T[2]

    @property
    def bounding(self):
        x_Coord, y_Coord, z_Coord = self.pos.T
        return np.array([
            [x_Coord.min(), x_Coord.max()],
            [y_Coord.min(), y_Coord.max()],
            [z_Coord.min(), z_Coord.max()]
        ])

    @property
    def bounding_x(self):
        x_Coord = self.pos_x
        return np.array([x_Coord.min(), x_Coord.max()])

    @property
    def bounding_y(self):
        y_Coord = self.pos_y
        return np.array([y_Coord.min(), y_Coord.max()])

    @property
    def bounding_z(self):
        z_Coord = self.pos_z
        return np.array([z_Coord.min(), z_Coord.max()])

    def fixBoundary(self):
        '''
        自动对模型赋予基本的静力计算边界条件。
        即x、y向边界约束相应的平动自由度，z负向（模型底）完全约束，z正向自由
        '''
        x_Coord, y_Coord, z_Coord = self.pos.T
        bounding = self.bounding
        xPosMask = abs(x_Coord - bounding[0][1]) < gc.param['geom_tol']
        xNegMast = abs(x_Coord - bounding[0][0]) < gc.param['geom_tol']
        yPosMask = abs(y_Coord - bounding[1][1]) < gc.param['geom_tol']
        yNegMask = abs(y_Coord - bounding[1][0]) < gc.param['geom_tol']
        zPosMask = abs(z_Coord - bounding[2][1]) < gc.param['geom_tol']
        zNegMask = abs(z_Coord - bounding[2][0]) < gc.param['geom_tol']
        fixity = gpa.fixity()
        fixity[np.logical_or(xPosMask, xNegMast)] = np.logical_or(fixity[np.logical_or(xPosMask, xNegMast)],
                                                                  np.array([True, False, False]))
        fixity[np.logical_or(yPosMask, yNegMask)] = np.logical_or(fixity[np.logical_or(yPosMask, yNegMask)],
                                                                  np.array([False, True, False]))
        fixity[zNegMask] = np.logical_or(fixity[zNegMask], np.array([True, True, True]))
        gpa.set_fixity(fixity)

    def swap_y_z(self, offset):
        '''
        交换y和z轴，适应abaqus建模习惯
        '''
        gridCoord = self.pos
        gpa.set_pos(np.vstack(
            (gridCoord[:, 0].T + offset[0], -1.0 * gridCoord[:, 2].T + offset[1], gridCoord[:, 1].T + offset[2])).T)