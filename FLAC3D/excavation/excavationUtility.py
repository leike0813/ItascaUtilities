# -*- coding: utf-8 -*-
import itasca as it
from ..customFunctions import generateGroupRangePhrase, generateRangePhrase
from ..zone.zoneUtility import ZoneUtility
from ..model.abstractSubUtility import AbstractSubUtility
from excavationGroup import ExcaGroup
from .. import globalContainer as gc


__all__ = ['ExcavationUtility']

class ExcavationUtility(AbstractSubUtility):
    """
    20220325：*开挖控制迭代器的序列化及反序列化策略仍需考虑，暂时不可靠。
    """

    def __init__(self, model=None):
        super(ExcavationUtility, self).__init__(model)
        self.__excaGroupList = []
        self.__currentStep = 0
        self.__excaSeq = []
        self.__excaSeqDelay_Step = []
        self.excaIter = None
        self._parameter_Setted = False
        # self.primMask = False
        # self.permMask = False
        # self.secMask = False

    def __getstate__(self):
        state = self.__dict__.copy()
        # state['excaSeq_Restore'] = self.excaSequence
        # state.pop('_ExcavationUtility__excaSeq')
        # state.pop('_ExcavationUtility__excaSeqDelay_Step')
        state.pop('excaIter')
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        # self.__excaSeq = []
        # self.__excaSeqDelay_Step = []
        self.initExcaProcess()

    @property
    def n_ExcaGroups(self):
        return len(self.__excaGroupList)

    @property
    def excaGroups(self):
        return self.__excaGroupList

    @property
    def n_ExcaPhases(self):
        return len(self.__excaSeq)

    @property
    def currentStep(self):
        return self.__currentStep

    @property
    def excaSequence(self):
        return {str(i) + ': ' + self.__excaSeq[i].__name__: 'Delay: ' + str(self.__excaSeqDelay_Step[i]) + 'steps' for i
                in range(self.n_ExcaPhases)}

    @staticmethod
    def custom_ExcaCommand(command_):
        def custom_ExcaCommand_Step(n_Step):
            it.command(command_)

        return custom_ExcaCommand_Step

    @staticmethod
    def custom_ExcaFunction(func, *args, **kwargs):
        def custom_ExcaFunction_Step(n_Step):
            func(*args, **kwargs)

        return custom_ExcaFunction_Step

    def get_Y_Bound(self, step):
        if step < 0:
            return [self.y_BoundList[0][0] - gc.param['geom_tol'], self.y_BoundList[0][0] - gc.param['geom_tol']]
        elif step > self.n_ExcaStep - 1:
            return [self.y_BoundList[self.n_ExcaStep - 1][1] + gc.param['geom_tol'],
                    self.y_BoundList[self.n_ExcaStep - 1][1] + gc.param['geom_tol']]
        else:
            return self.y_BoundList[step]

    def setExcaParameters(self, step_Length, step_Cycle):
        self.step_Length = step_Length
        self.step_Cycle = step_Cycle
        gpBound_y_ = self.modelUtil.gpUtil.bounding_y
        self.n_ExcaStep = int((gpBound_y_[1] - gpBound_y_[0] + 2 * gc.param['geom_tol']) // self.step_Length)
        self.y_BoundList = [
            [
                gpBound_y_[0] + i * self.step_Length, gpBound_y_[0] + (i + 1) * self.step_Length
            ] for i in range(self.n_ExcaStep)
        ]
        self._parameter_Setted = True

    def newExcaGroup(self, y_Bound_Global, groupList, slotName, _assignModel=True):
        excaGroup = ExcaGroup(y_Bound_Global, groupList, slotName, self, _assignModel)
        self.__excaGroupList.append(excaGroup)
        return excaGroup

    def addExcaSequence(self, excaFunc, excaDelay_Step=0):
        self.__excaSeq.append(excaFunc)
        self.__excaSeqDelay_Step.append(excaDelay_Step)

    def deleteExcaSequence(self, excaStepInd):
        self.__excaSeq.pop(excaStepInd)
        self.__excaSeqDelay_Step.pop(excaStepInd)

    def cycle_Wrapper_Step(self, dummy):
        def cycle(step):
            it.command('model cycle ' + str(step))

        return cycle(self.step_Cycle)

    cycle = cycle_Wrapper_Step

    def exca_SingleStep(self):
        for i in range(self.n_ExcaPhases):
            self.__excaSeq[i](self.__currentStep - self.__excaSeqDelay_Step[i])
        self.__currentStep += 1
        it.fish.set('ExcaStep', self.__currentStep)
        it.fish.set('ExcaDistance', self.__currentStep * self.step_Length)

    def initExcaProcess(self):
        def excaIter_Generator():
            while self.__currentStep < self.n_ExcaStep:
                yield self.exca_SingleStep()
            return

        if self._parameter_Setted:
            it.fish.set('ExcaStep', self.__currentStep)
            it.fish.set('ExcaDistance', self.__currentStep * self.step_Length)
            self.excaIter = excaIter_Generator()
        else:
            self.excaIter = None

    def exca_Next(self):
        try:
            next(self.excaIter)
        except StopIteration:
            print('Excavation finished.')

    def exca_To(self, step):
        while self.__currentStep < step:
            try:
                next(self.excaIter)
            except StopIteration:
                print('Excavation finished.')
                return

    def exca_Through(self):
        for i in range(self.__currentStep, self.n_ExcaStep):
            next(self.excaIter)
        print('Excavation finished.')

    @staticmethod
    def exca(y_Bound, groupList, cModel, propertyDict):
        ZoneUtility.assignMaterial(
            cModel,
            propertyDict,
            'group {groupPhrase} {rangePhrase}'.format(
                groupPhrase=generateGroupRangePhrase(groupList),
                rangePhrase=generateRangePhrase(ypos=y_Bound)
            )
        )