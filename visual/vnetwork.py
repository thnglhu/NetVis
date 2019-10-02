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

    @abstractmethod
    def modify(self, info):
        pass

    def load(self):
        super().load()
        # att = self.attributes

    def display(self, canvas):
        canvas.create_mapped_image(self, self['x'], self['y'], image=self['image'].get_image(), tag=tuple(self['tag']))
        self['image'].subscribe(self, self.reconfigure, canvas)

    def reconfigure(self, canvas):
        self.reallocate(canvas)
        canvas.itemconfig_mapped(self, image=self['image'].get_image(), tag=tuple(self['tag']))


class PC(VVertex, dv.Host):
    def __init__(self, ig_vertex, interface, **kwargs):
        VVertex.__init__(self, ig_vertex)
        dv.Host.__init__(self, interface, **kwargs)

    def _set_image(self):
        att = self.attributes
        att['image'] = resource.get_image("pc-on")
        att['deactivate'] = resource.get_image("pc-on")
        att['activate'] = resource.get_image("pc-on-focus")

    def info(self):
        return {
            'type': 'host',
            'name': self.name,
            'interface': self.interface.info(),
            'arp table': self.arp_table
        }

    def focus(self, canvas):
        self['image'] = self['activate']
        self.reconfigure(canvas)

    def unfocus(self, canvas):
        self['image'] = self['deactivate']
        self.reconfigure(canvas)

    def modify(self, info):
        self.name = info['name']
        self.interface.modify_device(info['interface'])


class Switch(VVertex, dv.Switch):
    def __init__(self, ig_vertex, **kwargs):
        VVertex.__init__(self, ig_vertex)
        dv.Switch.__init__(self, **kwargs)

    def _set_image(self):
        att = self.attributes
        att['image'] = resource.get_image("switch")

    def info(self):
        return {
            'type': 'switch',
            'name': self.name,
            'mac table': self.__get_mac_table()
        }

    def __get_mac_table(self):
        return {str(k): v.name for k, v in self.mac_table.items()}

    def modify(self, info):
        print(info)


class Router(VVertex, dv.Router):
    def __init__(self, ig_vertex, *interfaces, **kwargs):
        VVertex.__init__(self, ig_vertex)
        dv.Router.__init__(self, *interfaces, **kwargs)

    def _set_image(self):
        att = self.attributes
        att['image'] = resource.get_image("router")

    def info(self):
        return {
            'type': 'router',
            'name': self.name,
            'arp table': self.arp_table,
            'routing table': self.__get_routing_table()
        }

    def __get_routing_table(self):
        return {str(k): v.name for k, v in self.routing_table.items()}

    def modify(self, info):
        print(info)

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

    def unfocus(self, canvas): pass

    def info(self):
        return {
            'type': 'frame'
        }

classification = dict()
classification['pc'] = PC
classification['switch'] = Switch
classification['router'] = Router
