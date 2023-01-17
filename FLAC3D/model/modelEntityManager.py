# -*- coding: utf-8 -*-
import itasca as it
from ..bolt.bolt import BoltRingEntity

__all__ = ['ModelEntityManager']


class ModelEntityManager:
    _instance = None
    def __new__(cls, new=False, *args, **kw):
        '''
        令ModelEntityManager成为singleton
        '''
        if new or cls._instance is None:
            cls._instance = object.__new__(cls, new, *args, **kw)
        return cls._instance

    def __init__(self, model):
        self.Node = NodeManager(self)
        self.Element = ElementManager(self)
        self.Link = LinkManager(self)
        self.modelUtil = model
        self.archRingEntityList = []
        self.boltRingEntityList = []
        self.pileRoofRingEntityList = []
        self.tbmEntityList = []

    def createArchRingEntity(self):
        pass

    def createBoltRingEntity(self, y_Coord, boltRing):
        _boltRingEntity = BoltRingEntity(y_Coord, boltRing, self, self)
        self.boltRingEntityList.append(_boltRingEntity)
        boltRing._instances.append(_boltRingEntity)
        return _boltRingEntity


class AbstractSubManager(object):
    def __init__(self, manager):
        self.manager = manager
        # 由管理对象id至孪生实体对象的映射字典
        self.mappingDict = {}
        # 由Itasca cid至孪生实体对象的映射字典
        self.reverseMappingDict = {}

    def __call__(self):
        return self.mappingDict

    def add(self, subject):
        self.mappingDict[subject.ID] = subject
        self.reverseMappingDict[subject._cid] = subject

    def find(self, _cid):
        """由给定的Itasca cid，根据反向映射字典返回孪生实体对象"""
        return self.reverseMappingDict.get(_cid)

    def list(self):
        """Itasca自带list()接口的类比，返回由manager管理的所有孪生实体对象构成的迭代器"""
        return iter(self.mappingDict.values())


class NodeManager(AbstractSubManager):
    def near(self, coord):
        """
        根据坐标搜索对象并返回孪生实体对象（节点）
        参数coord必须为(x,y,z)坐标构成的三元组或Itasca vec3对象
        """
        return self.find(it.structure.node.near(coord).component_id())

    @classmethod
    def count(cls):
        """Itasca自带接口的副本"""
        return it.structure.node.count()

    @classmethod
    def maxid(cls):
        """Itasca自带接口的副本"""
        return it.structure.node.maxid()


class ElementManager(AbstractSubManager):
    def near(self, coord):
        """
        根据坐标搜索对象并返回孪生实体对象（单元）
        参数coord必须为(x,y,z)坐标构成的三元组或Itasca vec3对象
        """
        return self.find(it.structure.near(coord).component_id())

    @classmethod
    def count(cls):
        """Itasca自带接口的副本"""
        return it.structure.count()

    @classmethod
    def maxid(cls):
        """Itasca自带接口的副本"""
        return it.structure.maxid()


class LinkManager(AbstractSubManager):
    @classmethod
    def count(cls):
        """Itasca自带接口的副本"""
        return it.structure.link.count()

    @classmethod
    def maxid(cls):
        """Itasca自带接口的副本"""
        return it.structure.link.maxid()

