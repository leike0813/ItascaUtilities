# -*- coding: utf-8 -*-
import itasca as it
import numpy as np
from customDecorators import convert_Group_To_GroupList
import globalContainer as gc
try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable


__all__ = [
    'numpyArray2FishArray',
    'generatePropertyPhrase',
    'generateGroupRangePhrase',
    'generateRangePhrase',
    'generateFixityPhrase'
]

def numpyArray2FishArray(arr, name):
    _shape = list(np.array(arr.shape))
    _ndim = arr.ndim
    _nele = len(arr.flat)
    _iter = np.nditer(arr, flags = ['multi_index'])
    _index = []
    for i in range(_nele):
        _index.append(_iter.multi_index)
        _iter.iternext()
    it.command('[' + name + ' = array.create(' + str(_shape)[1: -1] + ')]')
    for i in range(len(arr.flat)):
        it.command('[' + name + '(' + str(list(np.array(_index[i]) + 1))[1: -1] + ') = ' + str(arr[_index[i]]) + ']')

def generatePropertyPhrase(_dict):
    propertyPhrase = ''
    for _name, _value in _dict.items():
        propertyPhrase += _name + ' ' + str(_value) + ' '
    propertyPhrase = propertyPhrase[:-1]
    return propertyPhrase

@convert_Group_To_GroupList
def generateGroupRangePhrase(groupName_or_List):
    groupPhrase = '"' + groupName_or_List[0] + '"'
    for i in range(1, len(groupName_or_List)):
        groupPhrase += ' or "' + groupName_or_List[i] + '"'
    return groupPhrase

def generateRangePhrase(xpos=None, ypos=None, zpos=None, cyl=None, id=None):
    rangeElementList = []
    if xpos is not None: # 这里必须这么写，否则数值0会被认为是False
        if isinstance(xpos, Iterable):
            if len(xpos) == 2:
                _xpos_lower = xpos[0] - gc.param['geom_tol']
                _xpos_upper = xpos[1] + gc.param['geom_tol']
            else:
                raise ValueError
        else:
            _xpos_lower = xpos - gc.param['geom_tol']
            _xpos_upper = xpos + gc.param['geom_tol']
        rangeElementList.append(
            'position-x {_xpos_lower} {_xpos_upper}'.format(
                _xpos_lower=_xpos_lower,
                _xpos_upper=_xpos_upper
            )
        )
    if ypos is not None:
        if isinstance(ypos, Iterable):
            if len(ypos) == 2:
                _ypos_lower = ypos[0] - gc.param['geom_tol']
                _ypos_upper = ypos[1] + gc.param['geom_tol']
            else:
                raise ValueError
        else:
            _ypos_lower = ypos - gc.param['geom_tol']
            _ypos_upper = ypos + gc.param['geom_tol']
        rangeElementList.append(
            'position-y {_ypos_lower} {_ypos_upper}'.format(
                _ypos_lower=_ypos_lower,
                _ypos_upper=_ypos_upper
            )
        )
    if zpos is not None:
        if isinstance(zpos, Iterable):
            if len(zpos) == 2:
                _zpos_lower = zpos[0] - gc.param['geom_tol']
                _zpos_upper = zpos[1] + gc.param['geom_tol']
            else:
                raise ValueError
        else:
            _zpos_lower = zpos - gc.param['geom_tol']
            _zpos_upper = zpos + gc.param['geom_tol']
        rangeElementList.append(
            'position-z {_zpos_lower} {_zpos_upper}'.format(
                _zpos_lower=_zpos_lower,
                _zpos_upper=_zpos_upper
            )
        )
    if cyl:
        if len(cyl) == 3 and len(cyl[0]) == 3 and len(cyl[1]) == 3:
            if isinstance(cyl[2], Iterable):
                if len(cyl[2]) == 2:
                    _radius = '{_radius_lower} {_radius_upper}'.format(
                        _radius_lower=cyl[2][0] - gc.param['geom_tol'],
                        _radius_upper=cyl[2][1] + gc.param['geom_tol']
                    )
                else:
                    raise ValueError
            else:
                _radius = '{_radius}'.format(_radius=cyl[2])
        else:
            raise ValueError
        rangeElementList.append(
            'cylinder end-1 {x0} {y0} {z0} end-2 {x1} {y1} {z1} radius {radius}'.format(
                x0=cyl[0][0], y0=cyl[0][1], z0=cyl[0][2],
                x1=cyl[1][0], y1=cyl[1][1], z1=cyl[1][2],
                radius=_radius
            )
        )
    if id is not None:
        if type(id) is int:
            rangeElementList.append(
                'id {_id}'.format(_id=id)
            )
        else:
            raise ValueError
    rangePhrase = ''
    for re in rangeElementList:
        rangePhrase += re
        rangePhrase += ' '
    rangePhrase = rangePhrase[:-1]
    return rangePhrase

def generateFixityPhrase(xvel=False, yvel=False, zvel=False, xrot=False, yrot=False, zrot=False, mode=None):
    fixModeDict = {
        'X_Symm_Zone': ('velocity-x', ),
        'Y_Symm_Zone': ('velocity-y', ),
        'Z_Symm_Zone': ('velocity-z', ),
        'X_ASymm_Zone': ('velocity-y', 'velocity-z'),
        'Y_ASymm_Zone': ('velocity-x', 'velocity-z'),
        'Z_ASymm_Zone': ('velocity-x', 'velocity-y'),
        'X_Symm_Node': ('velocity-x', 'rotation-y', 'rotation-z'),
        'Y_Symm_Node': ('velocity-y', 'rotation-x', 'rotation-z'),
        'Z_Symm_Node': ('velocity-z', 'rotation-x', 'rotation-y'),
        'X_ASymm_Node': ('velocity-y', 'velocity-z', 'rotation-x'),
        'Y_ASymm_Node': ('velocity-x', 'velocity-z', 'rotation-y'),
        'Z_ASymm_Node': ('velocity-x', 'velocity-y', 'rotation-z'),
        'Encastre': ('velocity-x', 'velocity-y', 'velocity-z', 'rotation-x', 'rotation-y', 'rotation-z')
    }

    fixityElementList = []
    if not mode:
        if xvel:
            fixityElementList.append('velocity-x')
        if yvel:
            fixityElementList.append('velocity-y')
        if zvel:
            fixityElementList.append('velocity-z')
        if xrot:
            fixityElementList.append('rotation-x')
        if yrot:
            fixityElementList.append('rotation-y')
        if zrot:
            fixityElementList.append('rotation-z')
    elif mode in fixModeDict.keys():
        for fe in fixModeDict[mode]:
            fixityElementList.append(fe)
    else:
        raise ValueError
    fixityPhrase = ''
    for fe in fixityElementList:
        fixityPhrase += fe
        fixityPhrase += ' '
    fixityPhrase = fixityPhrase[:-1]
    return fixityPhrase