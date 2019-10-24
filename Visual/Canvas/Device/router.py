from .vertex import Vertex
from ..interface import Interface
from Resource import get_image
import ipaddress as ipa
from ..Frame.Data import hello, rip
from time import time, sleep
from threading import Thread
import setting


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
            'position': tuple(self.position),
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
            from ..Frame.Data import hello
            if self.attributes.get('rip'):
                if isinstance(frame.packet, hello.Hello):
                    if frame.packet.request:
                        interface = port.device
                        reply = hello.Hello(interface.ip_interface.ip, ipa.ip_address(frame.packet.source), False)
                        interface.send(reply)
                        return True
                    else:
                        self['rip']['neighbor'][str(frame.packet.source)] = {
                            'port': port,
                            'time': time()
                        }
                        return True
                elif isinstance(frame.packet, rip.RIP):
                    info = frame.packet.info
                    has = False
                    for rule in info:
                        if rule['network'] not in self['rip']['table'] \
                                or self['rip']['table'][rule['network']]['hop'] > rule['hop'] + 1:
                            self['rip']['table'][rule['network']] = {
                                'hop': rule['hop'] + 1,
                                'via': str(frame.packet.source),
                                'interface': port.device
                            }
                            has = True
                    if has:
                        self.update()
                    return True
            if frame.packet.destination == port.device.ip_interface.ip:
                return True
            else:
                if not frame.packet.destination:
                    return False
                if self.attributes.get('rip'):
                    for network, info in self['rip']['table'].items():
                        if frame.packet.destination in ipa.ip_network(network):
                            info['interface'].send(frame.packet, info['via'])
                            return True
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

    def __hello(self):
        wait_time = 4
        start_time = time()
        while not self.destroyed and self.active:
            if self.attributes.get('rip'):
                for interface in self.interfaces:
                    hello_packet = hello.Hello(interface.ip_interface.ip)
                    interface.broadcast(hello_packet)
            else:
                break
            while not self.destroyed and self.active:
                if setting.time_scale.get() == 0 or time() - start_time < wait_time * 100 / setting.time_scale.get():
                    sleep(0.01)
                else:
                    start_time = time()
                    break

    def __rip(self):
        wait_time = 3
        start_time = time()
        while not self.destroyed and self.active:
            if self.attributes.get('rip'):
                for neighbor, info in self['rip']['neighbor'].items():
                    interface = info['port'].device
                    rip_packet = rip.RIP(interface.ip_interface.ip, ipa.ip_address(neighbor), self['rip']['table'])
                    interface.send(rip_packet)
            else:
                break
            while not self.destroyed and self.active:
                if setting.time_scale.get() == 0 or time() - start_time < wait_time * 100 / setting.time_scale.get():
                    sleep(0.01)
                else:
                    start_time = time()
                    break

    def activate_rip(self):
        self['rip'] = {
            'neighbor': dict(),
            'table': {
                str(interface.ip_interface.network): {
                    'hop': 0,
                    'via': None,
                    'interface': interface
                }
                for interface in self.interfaces
            },
        }
        Thread(target=self.__hello).start()
        Thread(target=self.__rip).start()

    def deactivate_rip(self):
        self.attributes.pop('rip')
    # endregion
