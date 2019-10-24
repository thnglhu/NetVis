from .vertex import Vertex
from ..interface import Interface
from Resource import get_image
import ipaddress as ipa
from ..Frame.Data import Frame


class Router(Vertex):

    # region Canvas declaration
    def __init__(self, canvas, info):
        super().__init__(canvas)
        self.position = info['position']
        self.name = info['name']
        self.interfaces = {
            Interface(interface_info, self) for interface_info in info['interfaces']
        }
        shortcut = {
            interface.port.name: interface for interface in self.interfaces
        }
        self.routing_table = [
            {
                'network': ipa.ip_network(rule['network']),
                'next_hop': rule['next_hop'],
                'interface': shortcut[rule['interface']]
            } for rule in info['static_routing_table']
        ]
        self.type = 'router'
        self.active = info['status']
        if not self.active:
            for interface in self.interfaces:
                interface.port.disable()
        self['image'] = self['on-image'] if self.active else self['off-image']

    def _set_image(self):
        self['on-image'] = get_image('_router-on')
        self['off-image'] = get_image('_router-off')

    def get_ports(self):
        return {
            interface.port for interface in self.interfaces
        }

    def save(self):
        return {
            'type': self.type,
            'status': self.active,
            'name': self.name,
            'position': self.position,
            'interfaces': [
                interface.save() for interface in self.interfaces
            ],
            'static_routing_table': [
                {
                    'network': str(rule['network']),
                    'next_hop': rule['next_hop'],
                    'interface': rule['interface'].port.name
                } for rule in self.routing_table
            ]
        }

    def destroy(self, collector):
        super().destroy(collector)
        for interface in self.interfaces:
            interface.destroy(collector)

    def modify(self, info):
        self.name = info['name']
    # endregion

    # region Logical
    def receive(self, frame, port):
        if frame.packet:
            if frame.packet.destination == port.device.ip_interface.ip:
                return True
            else:
                for rule in self.routing_table:
                    if frame.packet.destination in rule['network']:
                        if str(frame.packet.destination) == str(rule['interface'].ip_interface.ip):
                            pass
                        elif rule['next_hop']:
                            rule['interface'].send(frame.packet, rule['next_hop'])
                        else:
                            rule['interface'].send(frame.packet)
                        return True
                else:
                    return False
        else:
            return False

    def enable(self):
        self.active = True
        for interface in self.interfaces:
            interface.port.enable()
        self['image'].unsubscribe(self)
        self['image'] = self['on-image']
        self['image'].subscribe(self, self.reconfigure)

    def disable(self):
        self.active = False
        for interface in self.interfaces:
            interface.port.disable()
        self['image'].unsubscribe(self)
        self['image'] = self['off-image']
        self['image'].subscribe(self, self.reconfigure)
    # endregion
