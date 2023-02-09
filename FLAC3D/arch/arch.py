# -*- coding: utf-8 -*-

import itasca as it
from ..structuralComponent.element import Element


__all__ = ['ArchElement']


class ArchElement(Element):
    def __init__(self, structuralElementID, ringNumber, subElementID, sequenceNumber, cid, nodes, parent, manager):
        super(ArchElement, self).__init__(Element.Beam, structuralElementID, ringNumber, subElementID, sequenceNumber, cid, nodes, parent, manager)

    def __repr__(self):
        return 'Arch element {cid} at {pos}'.format(
            cid=self.pointer.component_id(),
            pos=tuple(round(coord, 3) for coord in self.pointer.pos())
        )