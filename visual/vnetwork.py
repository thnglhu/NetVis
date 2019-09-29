from . import vgraph as vg
import resource
import tkinter as tk
import numpy as np
from abc import ABC, abstractmethod
from threading import Thread
import time


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


class Frame(vg.CanvasItem):
    rad = 10
    __thread = None

    def __init__(self, edge, is_inverted=False):
        super().__init__()
        att = self.attributes
        att['edge'] = edge
        att['percent'] = 0.0
        self.is_inverted = is_inverted
        self.load()

    def __animate(self, canvas):
        att = self.attributes
        while att['percent'] < 100.0:
            att['percent'] += 1
            self.load()
            self.reallocate(canvas)
            time.sleep(0.1)
        if att['percent'] > 100.0:
            att['percent'] = 100.0
            self.load()
            self.reallocate(canvas)

    def load(self):
        att = self.attributes
        att['start'] = np.array(att['edge'].packed_points()[:2])
        att['end'] = np.array(att['edge'].packed_points()[2:])
        if self.is_inverted:
            att['start'], att['end'] = att['end'], att['start']
        att['position'] = att['start'] + (att['end'] - att['start']) * att['percent'] / 100.0
        print(att['position'], att['start'], att['end'], att['percent'])

    def display(self, canvas):
        att = self.attributes
        self.__thread = Thread(target=self.__animate, args=(canvas,))
        canvas.create_mapped_circle(self, *att['position'], self.rad, fill='red', tag='frame')

    def start_animation(self):
        if self.__thread:
            self.__thread.start()
        else:
            print("Too soon to animate")

    def reallocate(self, canvas):
        att = self.attributes
        canvas.coords_mapped(self, *att['position'], self.rad)

    def reconfigure(self, canvas):
        canvas.itemconfig_mapped()

    def focus(self, canvas): pass

    def blur(self, canvas): pass


classification = dict()
classification['pc'] = PC
classification['switch'] = Switch
classification['router'] = Router
