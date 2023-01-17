# -*- coding: utf-8 -*-
import math
from ..customFunctions import  generatePropertyPhrase
from ..zone.zoneUtility import ZoneUtility
from .. import globalContainer as gc


__all__ = ['Material']

class Material(object):
    """
    Material是管理实体单元本构模型及参数的容器。
    Material的名称（name）可自由取定，但建议与FLAC3D模型中的实体单元分组（group）名称一致以实现自动映射。
    当涉及更为复杂的单元-材料映射关系时，可额外指定groupTupleList参数定义材料与group-slot的映射关系.
    groupTupleList为由FLAC3D模型中的（实体单元分组名，单元分组slot名）字符串二元组组成的列表。
    groupTupleList允许同一材料对应多个分组中的多个单元，例如混凝土等高复用率材料经常会用于模型的不同部位、不同阶段。
    若groupTupleList不为空时，自动映射功能优先以groupTuple为准，而不再考虑name。
    groupTupleList指定时，不检查其合法性（复数同名group同时从属于不同slot在FLAC3D中是不可能的）。
    未来将添加参数名称及必要参数校验功能。
    """
    def __init__(self, name, cModel, propertyDict, materialUtil, groupTupleList = []):
        self.materialUtil = materialUtil
        self.name = name
        self.groupTupleList = groupTupleList
        self.__cModel = cModel
        self.__propertyDict = propertyDict

    def __repr__(self):
        return 'Material: ' + self.name

    @property
    def cModel(self):
        return self.__cModel

    @property
    def propertyDict(self):
        return self.__propertyDict

    @property
    def propertyString(self):
        return generatePropertyPhrase(self.__propertyDict)

    def setMaterial(self, cModel, propertyDict):
        self.__cModel = cModel
        self.__propertyDict = propertyDict

    def setProperty(self, propName, value):
        self.__propertyDict[propName] = value

    def assignMaterial(self, range_):
        ZoneUtility.assignMaterial(self.__cModel, self.__propertyDict, range_)

    def convert_Mohr_to_CamClay(self, _Cc, _Cs, _e0, _OCR):
        if self.cModel.lower() == 'mohr-coulomb':
            return {
                'poisson': self.propertyDict['poisson'],
                'friction': self.propertyDict['friction'],
                'cu': self.propertyDict['cohesion'] / math.tan(
                    math.pi / 4 - math.radians(self.propertyDict['friction']) / 2
                ),
                'Cc': _Cc,
                'Cs': _Cs,
                'e0': _e0,
                'OCR': _OCR
            }
        else:
            return None

    mohr2CamClay = convert_Mohr_to_CamClay