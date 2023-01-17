# -*- coding: utf-8 -*-
from material import Material
from ..model.abstractSubUtility import AbstractSubUtility
from .. import globalContainer as gc


__all__ = ['MaterialUtility']

class MaterialUtility(AbstractSubUtility):
    """
    FLAC3D 6.0 材料实用工具。
    材料由MaterialUtil的实例管理。
    """

    def __init__(self, model=None):
        super(MaterialUtility, self).__init__(model)
        self.__materialDict = dict()

    @property
    def n_Materials(self):
        return len(self.__materialDict)

    @property
    def materials(self):
        return self.__materialDict

    @property
    def materialList(self):
        return self.__materialDict.keys()

    @property
    def propertyDicts(self):
        return {_name: _material.propertyDict for _name, _material in self.__materialDict.items()}

    @property
    def cModels(self):
        return {_name: _material.cModel for _name, _material in self.__materialDict.items()}

    def importMaterial(self, name, cModel, propertyDict, groupTupleList=[]):
        self.__materialDict[name] = Material(name, cModel, propertyDict, self, groupTupleList)

    def deleteMaterial(self, name):
        self.__materialDict.pop(name)