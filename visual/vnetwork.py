from . import vgraph as vg
import resource
import tkinter as tk
import numpy as np
from abc import ABC, abstractmethod


class VVertex(vg.Vertex, ABC):

    def __init__(self, ig_vertex):
        super().__init__(ig_vertex)
        self._set_image()

    @abstractmethod
    def _set_image(self):
        pass

    def load(self):
        super().load()
        # att = self.attributes

    def display(self, canvas):
        att = self.attributes
        print(att)
        canvas.create_mapped_image(self, att['x'], att['y'], image=att['image'], tag=tuple(att['tag']))

    def reallocate(self, canvas):
        att = self.attributes
        position = np.array((att['x'], att['y']))
        canvas.coords_mapped(self, att['x'], att['y'])

    def reconfigure(self, canvas):
        att = self.attributes
        self.reallocate(canvas)
        canvas.itemconfig_mapped(self, image=att['image'], tag=tuple(att['tag']))


class PC(VVertex):
    def _set_image(self):
        att = self.attributes
        att['image'] = resource.get_image("pc")
        att['size'] = att['image'].width(), att['image'].height()


class Switch(VVertex):
    def _set_image(self):
        att = self.attributes
        att['image'] = resource.get_image("switch")
        att['size'] = att['image'].width(), att['image'].height()


class Router(VVertex):
    def _set_image(self):
        att = self.attributes
        att['image'] = resource.get_image("router")
        att['size'] = att['image'].width(), att['image'].height()


classification = dict()
classification['pc'] = PC
classification['switch'] = Switch
classification['router'] = Router
