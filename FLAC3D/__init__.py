import itasca as it
import dill
import globalContainer
from model.modelUtility import ModelUtility
from customDecorators import step_Filter
from customFunctions import *


__all__ = [
    'ModelUtility',
    'globalContainer',
    'save',
    'restore',
    'new',
    '_update_ShieldLink',
    '_update_CutterHeadLink',
    'step_Filter',
    'generateRangePhrase',
    'generatePropertyPhrase',
    'generateGroupRangePhrase',
    'generateFixityPhrase'
]

def save(filename):
    it.command('model save "{filename}.f3sav"'.format(filename=filename))
    # it.fish.set('__ModelUtility__', dill.dumps(ModelUtility._instance))
    with open('{filename}.f3mod'.format(filename=filename), 'wb') as f:
        dill.dump(ModelUtility._instance, f)

def restore(filename):
    it.command('model restore "{filename}.f3sav"'.format(filename=filename))
    # if '_save_Model' not in it.state_callbacks()['save']:
    #     it.set_callback('_save_Model', 'save')
    # if ModelUtility._instance is None:
    #     ModelUtility._instance = dill.loads(it.fish.get('__ModelUtility__'))
    with open('{filename}.f3mod'.format(filename=filename), 'rb') as f:
        ModelUtility._instance = dill.load(f)
    return ModelUtility._instance

def new():
    ModelUtility._instance = None

def _update_ShieldLink():
    ModelUtility._instance.tbmUtil.shield.updateShieldLink_Step(ModelUtility._instance.tbmUtil.currentStep)

def _update_CutterHeadLink():
    ModelUtility._instance.tbmUtil.cutterHead.updateCutterHeadLink_Step(ModelUtility._instance.tbmUtil.currentStep)

# it.set_callback('_save_Model', 'save')
it.set_callback('new', 'new')