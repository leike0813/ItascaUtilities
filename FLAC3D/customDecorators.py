# -*- coding: utf-8 -*-
from functools import wraps
import numpy as np
import inspect
import sys


__all__ = ['y_Bound_Detect', 'n_Step_Detect', 'convert_Group_To_GroupList', 'step_Filter']

def y_Bound_Detect(argName):
    def decorated(meth):
        @wraps(meth)
        def method_With_y_Bound_Detect(self, *args, **kwargs):
            y_Bound = inspect.getcallargs(meth, self, *args, **kwargs).get(argName)
            if y_Bound[1] <= y_Bound[0]:
                y_Bound[0], y_Bound[1] = y_Bound[1], y_Bound[0]
            y_Bound[0] = max(y_Bound[0], self.modelUtil.gpUtil.bounding_y[0])
            y_Bound[1] = min(y_Bound[1], self.modelUtil.gpUtil.bounding_y[1])
            return meth(self, *args, **kwargs)
        return method_With_y_Bound_Detect
    return decorated

def n_Step_Detect(meth):
    @wraps(meth)
    def method_With_n_Step_Detect(self, *args, **kwargs):
        def dummy_Method(self, *args, **kwargs):
            """超出范围，什么都不做。"""
            pass
        n_Step = inspect.getcallargs(meth, self, *args, **kwargs).get('n_Step')
        if n_Step < 0 or n_Step > self.modelUtil.excaUtil.n_ExcaStep - 1:
            return dummy_Method(self, *args, **kwargs)
        return meth(self, *args, **kwargs)
    return method_With_n_Step_Detect

def convert_Group_To_GroupList(func):
    @wraps(func)
    def func_With_GroupList_Conversion(*args, **kwargs):
        groupName_or_List = inspect.getcallargs(func, *args, **kwargs).get('groupName_or_List')
        if sys.version[0] == '2':
            gNoL_Index = inspect.getargspec(func)[0].index('groupName_or_List')
        else:
            gNoL_Index = inspect.getfullargspec(func)[0].index('groupName_or_List')
        if type(groupName_or_List) is str:
            args_modified = (args[i] if i != gNoL_Index else [groupName_or_List] for i in range(len(args)))
        else:
            args_modified = args
        return func(*args_modified, **kwargs)
    return func_With_GroupList_Conversion

def step_Filter(func, step):
    """
    20220324:支持输入step列表（整数、整数构成的列表或ndarray，或整数构成的集合）
    """
    if type(step) is int:
        stepList = set([step])
    elif type(step) is list:
        stepList = set(step)
    elif type(step) is np.ndarray and step.ndim == 1:
        stepList = set(step)
    elif type(step) is set:
        stepList = step
    else:
        raise TypeError
    @wraps(func)
    def func_With_Step_Filting(*args, **kwargs):
        def dummy_Func(*args, **kwargs):
            """除指定步外什么都不做"""
            pass
        n_Step = inspect.getcallargs(func, *args, **kwargs).get('n_Step')
        if n_Step in stepList:
            return func(*args, **kwargs)
        return dummy_Func(*args, **kwargs)
    return func_With_Step_Filting