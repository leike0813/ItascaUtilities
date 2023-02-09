# -*- coding: utf-8 -*-
import itasca as it


__all__ = ['ModelEntityManager']


class ModelEntityManager(object):
    _instance = None
    def __new__(cls, new=False, *args, **kw):
        '''
        令ModelEntityManager成为singleton
        '''
        if new or cls._instance is None:
            cls._instance = object.__new__(cls, new, *args, **kw)
        return cls._instance

    def __init__(self, model):
        self.__modelUtil = model
        self.__nodeManager = NodeManager(self)
        self.__elementManager = ElementManager(self)
        self.__linkManager = LinkManager(self)
        self.__archManager = ArchManager(self)
        self.__boltManager = BoltManager(self)
        self.__pileRoofManager = PileRoofManager(self)
        self.__tbmManager = TBMManager(self)

    @property
    def modelUtil(self):
        return self.__modelUtil

    @property
    def nodeManager(self):
        return self.__nodeManager

    @property
    def elementManager(self):
        return self.__elementManager

    @property
    def linkManager(self):
        return self.__linkManager

    @property
    def archManager(self):
        return self.__archManager

    @property
    def boltManager(self):
        return self.__boltManager

    @property
    def pileRoofManager(self):
        return self.__pileRoofManager

    @property
    def tbmManager(self):
        return self.__tbmManager

    Model = modelUtil
    Node = nodeManager
    Elem = elementManager
    Link = linkManager
    Arch = archManager
    Bolt = boltManager
    PRoof = pileRoofManager
    TBM = tbmManager

    def addChind(self):
        pass


class AbstractSubManager(object):
    def __init__(self, manager):
        self.__manager = manager
        self.__modelUtil = manager.modelUtil

    @property
    def manager(self):
        return self.__manager

    @property
    def modelUtil(self):
        return self.__modelUtil

class AbstractComponentManager(AbstractSubManager):
    def __init__(self, manager):
        super(AbstractComponentManager, self).__init__(manager)
        # 由管理对象id至孪生实体对象的映射字典
        self.__mappingDict = {}
        # 由Itasca cid至孪生实体对象的映射字典
        self.__reverseMappingDict = {}

    def __call__(self, id):
        return self.get(id)

    def add(self, subject):
        self.__mappingDict[subject.id] = subject
        self.__reverseMappingDict[subject.cid] = subject

    def find(self, cid):
        """由给定的Itasca cid，根据反向映射字典返回孪生实体对象"""
        return self.__reverseMappingDict.get(cid)

    def get(self, id):
        """由给定的id，根据映射字典返回孪生实体对象"""
        return self.__mappingDict.get(id)

    def list(self):
        """Itasca自带list()接口的类比，返回由manager管理的所有孪生实体对象构成的迭代器"""
        return iter(self.__mappingDict.values())


class AbstractStructureManager(AbstractSubManager):
    def __init__(self, manager):
        super(AbstractStructureManager, self).__init__(manager)
        self.__instances = []

    @property
    def instances(self):
        return self.__instances

    def add(self, instance):
        self.instances.append(instance)

    addChild = add

    def count(self):
        return len(self.__instances)

class NodeManager(AbstractComponentManager):
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


class ElementManager(AbstractComponentManager):
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


class LinkManager(AbstractComponentManager):
    @classmethod
    def count(cls):
        """Itasca自带接口的副本"""
        return it.structure.link.count()

    @classmethod
    def maxid(cls):
        """Itasca自带接口的副本"""
        return it.structure.link.maxid()


class ArchManager(AbstractStructureManager):
    def __init__(self, manager):
        super(ArchManager, self).__init__(manager)


class BoltManager(AbstractStructureManager):
    def __init__(self, manager):
        super(BoltManager, self).__init__(manager)


class PileRoofManager(AbstractStructureManager):
    def __init__(self, manager):
        super(PileRoofManager, self).__init__(manager)


class TBMManager(AbstractStructureManager):
    def __init__(self, manager):
        super(TBMManager, self).__init__(manager)