# -*- coding: utf-8 -*-
import itasca as it
from ..customDecorators import *
from ..customFunctions import generateGroupRangePhrase, generatePropertyPhrase
from ..model.abstractSubUtility import AbstractSubUtility
from .. import globalContainer as gc


__all__ = ['MaterialSlot']


class MaterialSlot(AbstractSubUtility):
    """
    MaterialSlot管理模型group和MaterialUtil实例中各Material名称的映射关系。
    MaterialSlot中的slot名可与FLAC3D模型中的slot名不同，但建议取为相同slot名以实现自动映射功能。
    关键私有属性：mappingDict：记录group名称:material名称的映射关系，一对一；
               rangeMappingDict：记录material名称：group名称的映射关系，一对多。
    """
    def __init__(self, slotName, util): # MaterialSlot对应的是ZoneUtil
        super(MaterialSlot, self).__init__(util.modelUtil)
        self.slotName = slotName
        self.__util = util
        self.__mappingDict = dict()
        self.__rangeMappingDict = dict()

    @property
    def util(self):
        return self.__util

    @property
    def mappingDict(self):
        '''
        mappingDict中，key为group的名称，value为材料名称
        '''
        return self.__mappingDict

    @property
    def rangeMappingDict(self):
        '''
        rangeMappingDict中，key为材料名称，value为对应于该材料的所有group名称组成的列表
        '''
        return self.__rangeMappingDict

    @property
    def n_Group(self):
        return len(self.__mappingDict)

    @property
    def rangeGroups(self):
        return self.__mappingDict.keys()

    @property
    def materials(self):
        '''
        materials返回的字典中，key为材料名称，value为对应的Material类实例
        '''
        return {_name: self.modelUtil.materialUtil.materials[_name] for _name in self.__rangeMappingDict.keys()}

    @property
    def materials_Group(self):
        '''
        materials_Group返回的字典中，key为group名称，value为材料的Material类实例
        '''
        return {_group: self.modelUtil.materialUtil.materials[_name] for _group, _name in self.__mappingDict.items()}

    @property
    def materialList(self):
        return self.__rangeMappingDict.keys()

    @property
    def cModels(self):
        return {_name: self.modelUtil.materialUtil.materials[_name].cModel for _name in self.__rangeMappingDict.keys()}

    @property
    def cModels_Group(self):
        return {_group: self.modelUtil.materialUtil.materials[_name].cModel for _group, _name in self.__mappingDict.items()}

    @property
    def propertyDicts(self):
        return {_name: self.modelUtil.materialUtil.materials[_name].propertyDict for _name in self.__rangeMappingDict.keys()}

    @property
    def propertyDicts_Group(self):
        return {_group: self.modelUtil.materialUtil.materials[_name].propertyDict for _group, _name in self.__mappingDict.items()}

    @staticmethod
    def getModelSlotGroupList(modelSlotName):
        """
        返回给定slotName中包含的group名称组成的列表，用于自动映射功能。
        需对全部单元遍历，应避免在循环中频繁调用。
        """
        groupSet = set()
        for z in it.zone.list():
            groupSet.add(z.group(modelSlotName))
        return list(groupSet)

    @staticmethod
    @convert_Group_To_GroupList
    def getModelGroupMaterialModel_Exact(groupName_or_List):
        """
        返回给定group或group集合的当前本构模型名称组成的列表。
        需对全部单元遍历，应避免在循环中频繁调用。
        """
        modelSet = set()
        for z in it.zone.list():
            _flag = False
            for gr in groupName_or_List:
                if z.in_group(gr):
                    _flag = True
            if _flag:
                modelSet.add(z.model())
        return list(modelSet)

    @convert_Group_To_GroupList
    def map_Material_To_Group(self, materialName, groupName_or_List):
        # if type(groupName_or_List) is str:
        #    groupName_or_List = [groupName_or_List]
        for groupName in groupName_or_List:
            self.__mappingDict[groupName] = materialName
        if materialName in self.__rangeMappingDict.keys():
            self.__rangeMappingDict[materialName].extend(groupName_or_List)
        else:
            self.__rangeMappingDict[materialName] = groupName_or_List

    mapMat2Group = map_Material_To_Group

    def autoMapping(self):
        """
        group-material自动映射需满足以下条件：
        case I-当材料未指定groupTuple时：
            （1）材料的name属性需与欲映射的实体单元group名称一致。
            （2）欲映射的实体单元group从属的slot名称需与当前MaterialSlot的slotName属性一致；
            例：MaterialUtil中存有三个材料，材料A、B、C的name属性分别为'alpha'、'beta'和'gamma'。
               模型中存在名称为'alpha'、'gamma'、'beta'的三个group,'alpha'从属于solt'S1'，'beta'和'gamma'从属于slot'S2'。
               对slotName为'S1'的MaterialSlot应用autoMapping方法，则会在'S1'中添加材料A与group'alpha'的映射关系；
               对slotName为'S2'的MaterialSlot应用autoMapping方法，则会在'S2'中添加材料B与group'beta'、材料C与group'gamma'的映射关系；
        case II-当材料指定了groupTuple（groupTupleList不为空）时：
            （1）材料的groupTupleList[i][1]与当前MaterialSlot的slotName属性一致；
            （2）对于满足条件的i，groupTupleList[i][0]与欲映射的实体单元group名称一致；
            （3）欲映射的实体单元group从属的slot名称需与当前MaterialSlot的slotName属性一致。
            例：MaterialUtil中存有三个材料，材料A、B、C的groupTuple属性分别为（此时name属性随意）
                   材料A：[('alpha', 'S1')]
                   材料B：[('alpha', 'S2'), ('beta', 'S2')]
                   材料C：[('gamma', S2), ('delta', S3)]
               模型中存在名称为'alpha'、'gamma'、'beta'、'delta'的四个group,'alpha'从属于solt'S1'，'beta'和'gamma'从属于slot'S2'，'delta'从属于slot'S3'。
               对slotName为'S1'的MaterialSlot应用autoMapping方法，则会在'S1'中添加材料A与group'alpha'的映射关系；
               对slotName为'S2'的MaterialSlot应用autoMapping方法，则会在'S2'中添加材料B与group'beta'、材料C与group'gamma'的映射关系，但不会添加材料A与group'alpha'的映射关系，因为group'alpha'不从属于slot'S2'；
               对slotName为'S3'的MaterialSlot应用autoMapping方法，则会在'S3'中添加材料C与group'delta'的映射关系。此时材料C在MaterialSlot'S2'中对应于group'beta'，在MaterialSlot'S3'中对应于group'delta'。
        """
        modelGroupList = MaterialSlot.getModelSlotGroupList(self.slotName)
        for mat in self.modelUtil.materialUtil.materials.values():
            _name , _groupTupleList = mat.name, mat.groupTupleList
            if len(_groupTupleList) >= 1:
                for _groupTuple in _groupTupleList:
                    if _groupTuple[1] == self.slotName and _groupTuple[0] in modelGroupList:
                        self.map_Material_To_Group(_name, _groupTuple[0])
            else:
                if _name in modelGroupList:
                    self.map_Material_To_Group(_name, _name)

    def getSubSlot(self, rangeGroups):
        materialSlot = MaterialSlot(self.slotName + '_SubSlot', self.util)
        for gr in rangeGroups:
            materialSlot.map_Material_To_Group(self.mappingDict[gr], gr)
        return materialSlot

    def assignMaterials(self, range_, _assignModel = True):
        for _name, _groupList in self.__rangeMappingDict.items():
            if _assignModel:
                # it.command(
                #     'zone cmodel assign ' + self.materials[_name].cModel \
                #     + ' range group ' + generateGroupRangePhrase(_groupList) + ' ' + range_
                # )
                it.command(
                    'zone cmodel assign {cmodel} range group {groupPhrase} {rangePhrase}'.format(
                        cmodel=self.materials[_name].cModel,
                        groupPhrase=generateGroupRangePhrase(_groupList),
                        rangePhrase=range_
                    )
                )
            else:
                # 以下语句为调试用，实际计算中应注释以避免频繁遍历单元造成性能降低
                # _modelList = MaterialSlot.getModelGroupMaterialModel_Exact(_groupList)
                # if len(_modelList) != 1 or _modelList[0] != _name:
                #    raise RuntimeError
                pass
            if self.materials[_name].cModel.lower() != 'null':
                # it.command(
                #     'zone property ' + generatePropertyPhrase(self.materials[_name].propertyDict)\
                #     + ' range group ' + generateGroupRangePhrase(_groupList) + ' ' + range_
                # )
                it.command(
                    'zone property {propertyPhrase} range group {groupPhrase} {rangePhrase}'.format(
                        propertyPhrase=generatePropertyPhrase(self.materials[_name].propertyDict),
                        groupPhrase=generateGroupRangePhrase(_groupList),
                        rangePhrase=range_
                    )
                )