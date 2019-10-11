from . import vgraph as vg
import resource
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
        canvas.itemconfig_mapped(self, image=self['image'].get_image(), tag=tuple(self['tag']))

    def deep_destroy(self, canvas):
        graph = self.graph()
        graph.vertices.remove(self)
        canvas.remove(self)


class Host(VVertex, dv.Host):
    def __init__(self, ig_vertex, interface, **kwargs):
        VVertex.__init__(self, ig_vertex)
        dv.Host.__init__(self, interface, **kwargs)

    def _set_image(self):
        att = self.attributes
        att['image'] = resource.get_image("pc-on")
        att['deactivate'] = resource.get_image("pc-on")
        att['activate'] = resource.get_image("pc-on-focus")
        att['offline'] = resource.get_image('pc-off')

    def info(self):
        self.clean_cache()
        result = {
            'type': 'host',
            'name': self.name,
            'interface': self.interface.info(),
            'arp_table': [
                {
                    'ip_address': ip_address,
                    'mac_address': info['mac_address'],
                    'expire_time': info['time_stamp']
                } for ip_address, info in self.arp_table.items()
            ],
            'active': self.active,
        }
        return result

    def focus(self, canvas):
        if self.active:
            self['image'].unsubscribe(self)
            self['image'] = self['activate']
            self['image'].subscribe(self, self.reconfigure, canvas)
            self.reconfigure(canvas)

    def unfocus(self, canvas):
        if self.active:
            self['image'].unsubscribe(self)
            self['image'] = self['deactivate']
            self['image'].subscribe(self, self.reconfigure, canvas)
            self.reconfigure(canvas)

    def modify(self, info):
        self.name = info['name']
        self.interface.modify(info['interface'])

    def disable(self, canvas):
        self['image'] = self['offline']
        super().disable(canvas)

    def enable(self, canvas):
        self['image'] = self['deactivate']
        super().enable(canvas)

    def json(self):
        json = super().json()
        json['x'] = self['x']
        json['y'] = self['y']
        return json

    def deep_destroy(self, canvas):
        self.is_destroyed = True
        self['deactivate'].unsubscribe(self)
        self['activate'].unsubscribe(self)
        self['offline'].unsubscribe(self)
        if self.interface:
            self.interface.deep_destroy(canvas=canvas)
        super().deep_destroy(canvas)


class Switch(VVertex, dv.Switch):
    def __init__(self, ig_vertex, mac_address, **kwargs):
        VVertex.__init__(self, ig_vertex)
        dv.Switch.__init__(self, mac_address, **kwargs)

    def _set_image(self):
        att = self.attributes
        att['image'] = resource.get_image("switch")

    def info(self):
        result = {
            'type': 'switch',
            'mac_address': self.mac_address,
            'name': self.name,
            'mac_table': self.__get_mac_table(),
            'root_id': self.root_id,
            'bridge_id': id(self),
            'status': {
                key.name: value['status'] for key, value in self.ports.items()
            },
            'active': self.active,
        }
        if self.stp:
            result['STP'] = {
                'id': id(self),
                'root_id': self.root_id,
                'cost': self.cost,
            }
        return result

    def __get_mac_table(self):
        return {str(k): v.name for k, v in self.mac_table.items()}

    def modify(self, info):
        self.name = info['name']

    def json(self):
        json = super().json()
        json['x'] = self['x']
        json['y'] = self['y']
        return json

    def deep_destroy(self, canvas):
        self.is_destroyed = True
        self['image'].unsubscribe(self)
        print(self.others)
        for other in self.others.copy():
            my_device = self.device
            other_device = other.device
            edges = my_device.link_edges.intersection(other_device.link_edges)
            for edge in edges:
                edge.deep_destroy(canvas)
        super().deep_destroy(canvas)


class Router(VVertex, dv.Router):
    def __init__(self, ig_vertex, *interfaces, **kwargs):
        VVertex.__init__(self, ig_vertex)
        dv.Router.__init__(self, *interfaces, **kwargs)

    def _set_image(self):
        att = self.attributes
        att['image'] = resource.get_image("router")

    def info(self):
        result = {
            'type': 'router',
            'name': self.name,
            # 'arp_table': self.arp_table,
            'arp_table': [
                {
                    'ip_address': str(ip_address),
                    'mac_address': mac_address
                } for value in self.arp_table.values() for ip_address, mac_address in value.items()
            ],
            # 'interfaces': dict(enumerate(map(lambda interface: interface.name, self.interfaces))),
            'interfaces': [interface.info() for interface in self.interfaces],
            'routing_table': {
                str(key): value for key, value in self.routing_table.items()
            },
            'active': self.active,
        }
        if self.extend.get('RIP'):
            result['RIP_routing_table'] = [
                {
                    'ip_network': network,
                    'via': info['via'],
                    'hop': info['hop'],
                } for network, info in self.extend['RIP']['table'].items()
            ]
        return result

    def modify(self, info):
        import ipaddress as ipa
        self.name = info['name']
        self.routing_table = {
            ipa.ip_network(destination): {
                'next_hop': next_hop,
                'interface': self.get_interface_by_ip(interface),
                'type': _type
            } for destination, next_hop, interface, _type in info['routing_table']
        }

    def json(self):
        json = super().json()
        json['x'] = self['x']
        json['y'] = self['y']
        return json

    def deep_destroy(self, canvas):
        self.is_destroyed = True
        self['image'].unsubscribe(self)
        for interface in self.interfaces:
            interface.deep_destroy(canvas=canvas)
        super().deep_destroy(canvas)


class Frame(vg.CanvasItem):
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
        self['image'] = kwargs.get('image')
        self.speed = kwargs.get('speed', 10)
        self.name = kwargs.get('name')
        canvas = kwargs.get('canvas')
        if canvas:
            from visual import visible
            if not visible.get(self.name):
                self.trigger()
            else:
                self.display(canvas)
                self.start_animation()

    def __animate(self, canvas):
        from visual import visible
        att = self.attributes
        while att['percent'] < 100.0 \
                and self.active \
                and not self['edge'].is_destroyed \
                and not self.is_destroyed \
                and visible.get(self.name):
            att['percent'] += self.speed / 2
            if att['percent'] > 100.0:
                att['percent'] = 100
            self.load()
            self.reallocate(canvas)
            time.sleep(0.025)

        if self.active and not self['edge'].is_destroyed and not self.is_destroyed:
            if not visible.get(self.name):
                time.sleep(0.05)
                self.trigger()
                canvas.remove(self)
                return
            if att['percent'] > 100.0:
                att['percent'] = 100.0
                self.load()
                self.reallocate(canvas)
            self.trigger()
        canvas.remove(self)

    def trigger(self):
        if self.func:
            self.func(*self.params)

    def load(self):
        att = self.attributes
        att['start'] = np.array(att['edge'].packed_points()[:2])
        att['end'] = np.array(att['edge'].packed_points()[2:])
        if self.is_inverted:
            att['start'], att['end'] = att['end'], att['start']
        att['position'] = att['start'] + (att['end'] - att['start']) * att['percent'] / 100.0

    def display(self, canvas):
        self.__thread = Thread(target=self.__animate, args=(canvas,))
        canvas.create_mapped_image(self, *self['position'], image=self['image'].get_image(), tag='frame')
        self['image'].subscribe(self, self.reconfigure, canvas)

    def start_animation(self):
        if self.__thread:
            self.__thread.start()
        else:
            print("Too soon to animate")

    def reallocate(self, canvas):
        att = self.attributes
        canvas.coords_mapped(self, *att['position'])

    def reconfigure(self, canvas):
        canvas.itemconfig_mapped(image=self['image'].get_image())

    def focus(self, canvas): pass

    def unfocus(self, canvas): pass

    def destroy(self, canvas):
        self.active = False
        self['image'].unsubscribe(self)

    def deep_destroy(self, canvas):
        self.destroy(canvas)
        self.is_destroyed = True
        canvas.remove(self)

    def info(self):
        return {
            'type': 'frame'
        }


classification = dict()
classification['host'] = Host
classification['switch'] = Switch
classification['router'] = Router
