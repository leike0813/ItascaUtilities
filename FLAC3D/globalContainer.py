# -*- coding: utf-8 -*-
try:
    from enum import Enum
except ImportError:
    class Enum(object):
        pass

__all__ = ['parameters', 'ModelType']

parameters = {
    'geom_tol': 1e-3,
    'eid_base_offset': 900
}

param = parameters

class ModelType(Enum):
    half_Model = 1
    full_Model = 0