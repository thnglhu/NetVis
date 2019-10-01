from . import vgraph as vg
import resource
import tkinter as tk
import numpy as np
from abc import ABC, abstractmethod
from threading import Thread
from network import devices as dv
import time


class VVertex(vg.Vertex, ABC):
    active = True
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
        # print(att)
        canvas.create_mapped_image(self, att['x'], att['y'], image=att['image'], tag=tuple(att['tag']))

    def reconfigure(self, canvas):
        att = self.attributes
        self.reallocate(canvas)
        canvas.itemconfig_mapped(self, image=att['image'], tag=tuple(att['tag']))


class PC(VVertex, dv.Host):
    def __init__(self, ig_vertex, interface, **kwargs):
        VVertex.__init__(self, ig_vertex)
        dv.Host.__init__(self, interface, **kwargs)

    def _set_image(self):
        att = self.attributes
        att['image'] = resource.get_image("pc-on")
        att['size'] = att['image'].width(), att['image'].height()

    def info(self):
        return {
            'type': 'host',
            'name': self.name,
            'interface': self.interface.name,
            'arp table': self.arp_table
        }


class Switch(VVertex, dv.Switch):
    def __init__(self, ig_vertex, **kwargs):
        VVertex.__init__(self, ig_vertex)
        dv.Switch.__init__(self, **kwargs)

    def _set_image(self):
        att = self.attributes
        att['image'] = resource.get_image("switch")
        att['size'] = att['image'].width(), att['image'].height()

    def info(self):
        return {
            'type': 'switch',
            'name': self.name,
            'mac table': self.__get_mac_table()
        }

    def __get_mac_table(self):
        return {str(k): v.name for k, v in self.mac_table.items()}


class Router(VVertex, dv.Router):
    def __init__(self, ig_vertex, *interfaces, **kwargs):
        VVertex.__init__(self, ig_vertex)
        dv.Router.__init__(self, *interfaces, **kwargs)

    def _set_image(self):
        att = self.attributes
        att['image'] = resource.get_image("router")
        att['size'] = att['image'].width(), att['image'].height()

    def info(self):
        return {
            'type': 'switch',
            'name': self.name,
            'arp table': self.arp_table,
            'routing table': self.__get_routing_table()
        }

    def __get_routing_table(self):
        return {str(k): v.name for k, v in self.routing_table.items()}


class Frame(vg.CanvasItem):
    rad = 10
    __thread = None

    def __init__(self, edge, func=None, params=(), is_inverted=False, **kwargs):
        super().__init__()
        att = self.attributes
        att['edge'] = edge
        att['percent'] = 0.0
        self.is_inverted = is_inverted
        self.load()
        self.func = func
        self.params = params
        self.color = kwargs.get('fill')

    def __animate(self, canvas):
        att = self.attributes
        while att['percent'] < 100.0:
            att['percent'] += 1
            self.load()
            self.reallocate(canvas)
            time.sleep(0.01)
        if att['percent'] > 100.0:
            att['percent'] = 100.0
            self.load()
            self.reallocate(canvas)
        if self.func:
            self.func(*self.params)
        canvas.remove(self)

    def load(self):
        att = self.attributes
        att['start'] = np.array(att['edge'].packed_points()[:2])
        att['end'] = np.array(att['edge'].packed_points()[2:])
        if self.is_inverted:
            att['start'], att['end'] = att['end'], att['start']
        att['position'] = att['start'] + (att['end'] - att['start']) * att['percent'] / 100.0

    def display(self, canvas):
        att = self.attributes
        self.__thread = Thread(target=self.__animate, args=(canvas,))
        canvas.create_mapped_circle(self, *att['position'], self.rad, fill=self.color, tag='frame')

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

    def info(self):
        return {
            'type': 'frame'
        }

classification = dict()
classification['pc'] = PC
classification['switch'] = Switch
classification['router'] = Router