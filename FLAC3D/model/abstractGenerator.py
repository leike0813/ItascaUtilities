# -*- coding: utf-8 -*-

__all__ = ['AbstractGenerator']


class AbstractGenerator(object):
    def __init__(self, instanceClass, model=None):
        self.__modelUtil = model
        self.instanceClass = instanceClass
        self.__instances = []
        self.instantiate_Param_List = []

    @property
    def modelUtil(self):
        return self.__modelUtil

    @property
    def instances(self):
        return self.__instances

    @property
    def n_Instance(self):
        return len(self.__instances)

    def instantiate(self, parent, *args, **kwargs):
        _instance = self.instanceClass(*args, parent=parent, generator=self, manager=self.modelUtil.entityManager,
                                       **kwargs)
        parent.addChild(_instance)
        _paramDict = {key: self.__dict__[key] for key in self.instantiate_Param_List}
        _instance.update_Param(_paramDict)
        self.__instances.append(_instance)
        self.registerInstance(_instance)
        return _instance

    def registerInstance(self, instance):
        pass


# class AbstractGenerator(type):
#     def __init__(cls, model=None, *args, **kwargs):
#         cls.__modelUtil = model
#         cls.__instances = []
#         super(AbstractGenerator, cls).__init__(*args, **kwargs)
#
#     @property
#     def modelUtil(cls):
#         return cls.__modelUtil
#
#     @property
#     def instances(cls):
#         return cls.__instances
#
#     @property
#     def n_Instance(cls):
#         return len(cls.__instances)
#
#
#     def __call__(cls, parent, *args, **kwargs):
#         _instance = super(AbstractGenerator, cls).__call__(*args, **kwargs)
#         setattr(_instance, '_AbstractEntity__parent', parent)
#         setattr(_instance, '_AbstractEntity__manager', cls.modelUtil.entityManager)
#         parent.addChild(_instance)
#         cls.__instances.append(_instance)
#         return _instance