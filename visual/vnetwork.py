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
        att = self.attributes
        print("+", att)
        att['size'] = np.array((att['image'].width(), att['image'].height()))

    def display(self, canvas):
        att = self.attributes
        position = np.array((att['x'], att['y']))
        print(att['size'])
        canvas.create_mapped_image(self, *(position - att['size']/2), image=att['image'])

    def reallocate(self, canvas):
        att = self.attributes
        position = np.array((att['x'], att['y']))
        canvas.coords_mapped(self, *(position - att['size']/2))

    def reconfigure(self, canvas):
        att = self.attributes
        self.reallocate(canvas)
        canvas.itemconfig_mapped(self, image=att['image'])


class PC(VVertex):
    def _set_image(self):
        att = self.attributes
        att['image'] = resource.get_image("pc")
        att['size'] = att['image'].width(), att['image'].height()


class Swith(VVertex):
    def _set_image(self):
        att = self.attributes
        att['image'] = resource.get_image("switch")
        att['size'] = att['image'].width(), att['image'].height()


class Router(VVertex):
    def _set_image(self):
        att = self.attributes
        att['image'] = resource.get_image("router")
        att['size'] = att['image'].width(), att['image'].height()


