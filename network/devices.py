import ipaddress as ipa
from . import data
from visual import vnetwork as vn
from network import protocol_handler as ph
from functools import partial
from threading import Thread
import time

NIC = set()

class Interface:
    device = None
    name = 'unknown'

    def __init__(self, name, mac_address, ip_address, ip_network, default_gateway):
        self.other = None
        self.attachment = None
        self.params = []
        self.name = name
        self.mac_address = mac_address
        self.ip_address = ipa.ip_address(ip_address)
        self.ip_network = ipa.ip_network(ip_network)
        self.default_gateway = ipa.ip_address(default_gateway)
        NIC.add(self)

    @staticmethod
    def load(json):
        return Interface(
            json['name'],
            json['mac_address'],
            json['ip_address'],
            json['ip_network'],
            json['default_gateway']
        )

    def __str__(self):
        return self.name

    def info(self):
        return {
            'name': self.name,
            'mac_address': self.mac_address,
            'ip_address': self.ip_address,
            'ip_network': self.ip_network,
            'default_gateway': self.default_gateway,
        }

    def modify(self, info):
        self.name = info['name']
        self.mac_address = info['mac_address']
        self.ip_address = ipa.ip_address(info['ip_address'])
        self.ip_network = ipa.ip_network(info['ip_network'])
        self.default_gateway = info['default_gateway']

    def connect(self, other):
        self.other = other
        other.attach(self)

    def attach(self, other):
        self.other = other

    def disconnect(self, other, init=True):
        if other and other is self.other:
            if init:
                self.other.disconnect(self, False)
            else:
                self.other = None

    def attach_device(self, device):
        self.device = device

    def receive(self, source, frame, canvas=None):
        try:
            if not self.__getattribute__('active'):
                return
        except AttributeError:
            pass

        self.attachment(source, frame, canvas, *self.params)

    def send(self, frame, canvas=None):
        try:
            if not self.__getattribute__('active'):
                return
        except AttributeError:
            pass
        if self.other is None:
            return
        if canvas:
            my_device = self.device
            other_device = self.other.device
            edges = my_device.link_edges.intersection(other_device.link_edges)
            for edge in edges:
                is_inverted = not edge.points[0] == my_device
                image = frame.packet.get_image()
                speed = edge['bandwidth'] / frame.get_size() * 8
                f = vn.Frame(
                    edge,
                    self.other.receive,
                    (self, frame, canvas),
                    is_inverted,
                    image=image,
                    speed=speed,
                    name=frame.get_name(),
                    canvas=canvas
                )
        else:
            self.other.receive(self, frame, canvas)

    def json(self):
        return {
            'name': self.name,
            'id': id(self),
            'mac_address': self.mac_address,
            'ip_address': str(self.ip_address),
            'ip_network': str(self.ip_network),
            'default_gateway': str(self.default_gateway)
        }

    def deep_destroy(self, **kwargs):
        if self.other:
            my_device = self.device
            other_device = self.other.device
            edges = my_device.link_edges.intersection(other_device.link_edges)
            for edge in edges:
                edge.deep_destroy(kwargs.get('canvas'))
            self.disconnect(self.other)


class Host:
    def __init__(self, interface, **kwargs):
        if isinstance(interface, dict):
            interface = Interface(**interface)
        self.interface = interface
        interface.attach_device(self)
        interface.attachment = self.__receive
        if kwargs.get('arp_table'):
            self.arp_table = {
                #ipa.ip_address(key): value for key, value in self.arp_table.items()
                ipa.ip_address(info['ip_address']): {
                    'mac_address': info['mac_address'],
                    'time_stamp': info['expire_time'],
                } for info in kwargs.get('arp_table')
            }
        else:
            self.arp_table = dict()
        self.name = kwargs.get('name')
        self.__buffer = set()

    def send(self, canvas, ip_target, segment=None, init=True):
        try:
            if not self.__getattribute__('active'):
                return
        except AttributeError:
            pass
        if not init:
            buffer = (id(canvas), id(ip_target), id(segment))
            if buffer not in self.__buffer:
                return
            else:
                self.__buffer.remove(buffer)
        if not self.interface:
            print('No connection')
            return
        if self.cache_contains(ip_target):
            packet = data.ICMP(self.interface.ip_address, ip_target, self.interface, segment)
            frame = data.Frame(self.interface.mac_address, self.arp_table[ip_target]['mac_address'], packet)
        elif ip_target in self.interface.ip_network:
            self.__buffer.add((id(canvas), id(ip_target), id(segment)))
            function = partial(self.send, canvas, ip_target, segment, False)
            packet = data.ARP(self.interface.ip_address, ip_target, function)
            frame = data.BroadcastFrame(self.interface.mac_address, packet)
        elif self.cache_contains(self.interface.default_gateway):
            packet = data.ICMP(self.interface.ip_address, ip_target, self.interface, segment)
            frame = data.Frame(self.interface.mac_address,
                               self.arp_table[self.interface.default_gateway]['mac_address'], packet)
        else:
            self.__buffer.add((id(canvas), id(ip_target), id(segment)))
            function = partial(self.send, canvas, ip_target, segment, False)
            packet = data.ARP(self.interface.ip_address, self.interface.default_gateway, function)
            frame = data.BroadcastFrame(self.interface.mac_address, packet)
        self.interface.send(frame, canvas)

    def cache_arp(self, frame):
        if frame.mac_target == self.interface.mac_address:
            self.arp_table[frame.packet.ip_source] = {
                'mac_address': frame.mac_source,
                'time_stamp': time.time() + 30
            }

    def cache_contains(self, ip_address):
        if ip_address in self.arp_table:
            info = self.arp_table[ip_address]
            if time.time() <= info['time_stamp']:
                return True
            else:
                self.arp_table.pop(ip_address)
        return False

    def clean_cache(self):
        for ip_address in self.arp_table.copy():
            info = self.arp_table[ip_address]
            if time.time() > info['time_stamp']:
                self.arp_table.pop(ip_address)

    def fix_time_stamp(self, root_time_stamp):
        for ip_address, info in self.arp_table.items():
            info['time_stamp'] = time.time() + info['time_stamp'] - root_time_stamp

    def __receive(self, source, frame, canvas=None):
        try:
            if not self.__getattribute__('active'):
                return
        except AttributeError:
            pass

        self.cache_arp(frame)
        ph.interface_icmp_handler(self.interface, frame, source=source, canvas=canvas)
        ph.interface_arp_handler(self.interface, frame, source=source, canvas=canvas)

    def json(self):
        return {
            'type': 'host',
            'name': self.name,
            'interface': self.interface.json(),
            # 'arp_table': {
            #     str(key): value for key, value in self.arp_table.items()
            # },
            'arp_table': [
                {
                    'ip_address': str(ip_address),
                    'mac_address': info['mac_address'],
                    'expire_time': info['time_stamp']
                } for ip_address, info in self.arp_table.items()
            ]

        }


class Switch:
    def __init__(self, mac_address, **kwargs):
        self.mac_table = kwargs.get('mac_table') or dict()
        self.mac_address = mac_address
        self.device = self
        self.name = kwargs.get('name')
        self.ports = dict()
        self.others = set()
        self.stp = kwargs.get('stp', True)
        self.thread = None
        self.root_id = id(self)
        self.cost = 0

    def activate_stp(self, canvas):
        self.stp = True
        self.thread = Thread(target=self.__elect, args=(canvas,))
        self.thread.start()

    def send_elect(self, source, frame, canvas):

        for port, value in self.ports.copy().items():
            if value['status'] == 'root':
                continue
            # self.mac_table = dict()
            if port is not source and canvas:
                my_device = self.device
                other_device = value['interface'].device
                if hasattr(my_device, 'link_edges'):
                    edges = my_device.link_edges.intersection(other_device.link_edges)
                else:
                    return
                for edge in edges:
                    is_inverted = not edge.points[0] == my_device
                    image = frame.get_image()
                    speed = edge['bandwidth'] / frame.get_size() * 8
                    f = vn.Frame(
                        edge,
                        value['interface'].receive,
                        (self, frame, canvas),
                        is_inverted,
                        image=image,
                        speed=speed,
                        name=frame.get_name()
                    )
                    f.display(canvas)
                    f.start_animation()

    def __elect(self, canvas):
        from random import uniform
        time.sleep(uniform(1, 5))
        while True and not self.__getattribute__('is_destroyed'):
            if self.root_id == id(self):
                frame = data.STP(self.mac_address, self.root_id, self.root_id, self.cost)
                self.send_elect(None, frame, canvas)
            time.sleep(20)

    def disconnect(self, other, init=True):
        if other in self.others:
            self.others.remove(other)
            interface = None
            for key, value in self.ports.items():
                if value['interface'] == other:
                    interface = key
            if interface:
                other.disconnect(self, False)
                self.ports.pop(interface)

    def attach(self, other):
        self.others.add(other)
        self.ports[other] = {
            'interface': other,
            'status': 'designated'
        }

    def connect(self, other):
        self.others.add(other)
        self.ports[other] = {
            'interface': other,
            'status': 'designated'
        }
        other.attach(self)

    def receive(self, source, frame, canvas=None):
        try:
            if not self.__getattribute__('active'):
                return
        except AttributeError:
            pass
        if self.ports[source]['status'] == 'blocked':
            return
        # print(self.name, 'update mac table')
        self.mac_table[frame.mac_source] = source
        if isinstance(frame, data.STP) and self.stp:
            root_id, bridge_id, cost = frame.get_bpdu()
            if root_id < self.root_id:
                for port in self.ports.values():
                    port['status'] = 'designated'
                self.ports[source]['status'] = 'root'
                self.root_id = root_id
                self.cost = cost + 1
                next_frame = data.STP(self.mac_address, self.root_id, id(self), self.cost)
                self.send_elect(source, next_frame, canvas)
            elif root_id == self.root_id:

                if bridge_id == self.root_id:
                    self.ports[source]['status'] = 'root'
                elif (self.cost < cost or self.cost == cost and id(self) > bridge_id) \
                        and self.ports[source]['status'] != 'designated':
                    self.ports[source]['status'] = 'designated'
                elif self.ports[source]['status'] != 'root' and self.ports[source]['status'] != 'blocked':
                    self.ports[source]['status'] = 'blocked'
                elif id(self) < bridge_id:
                    return
                next_frame = data.STP(self.mac_address, self.root_id, id(self), self.cost)
                self.send_elect(source, next_frame, canvas)
            return

        elif isinstance(frame, data.BroadcastFrame) and not isinstance(frame, data.STP):
            ph.hub_broadcast_handler(self, frame, source=source, canvas=canvas)
        else:
            if frame.mac_target in self.mac_table and source != self.mac_table[frame.mac_target]:
                self.send(frame, self.mac_table[frame.mac_target], canvas)

    def send(self, frame, target=None, canvas=None):
        try:
            if not self.__getattribute__('active'):
                return
        except AttributeError:
            pass
        if target is None or target not in self.ports:
            return
        if self.ports[target]['status'] == 'blocked' and not isinstance(frame, data.STP):
            return
        if canvas:
            my_device = self.device
            other_device = target.device
            if hasattr(my_device, 'link_edges'):
                edges = my_device.link_edges.intersection(other_device.link_edges)
            else:
                return
            for edge in edges:
                is_inverted = not edge.points[0] == my_device
                image = frame.packet.get_image()
                speed = edge['bandwidth'] / frame.get_size() * 8
                f = vn.Frame(
                    edge,
                    target.receive,
                    (self, frame, canvas),
                    is_inverted,
                    image=image,
                    speed=speed,
                    name=frame.get_name(),
                    canvas=canvas
                )
            return
        target.receive(self, frame, canvas)

    def json(self):
        return {
            'type': 'switch',
            'id': id(self),
            'name': self.name,
            'mac_address': self.mac_address,
            'mac_table': {
                key: id(value) for key, value in self.mac_table.items()
            }
        }

    def set_mac_table(self, mac_table):
        self.mac_table = mac_table

    def cache_mac_address(self, frame, source):
        self.mac_table[frame.mac_source] = {
            'type': 'dynamic',
            'source': source,
            'time_stamp': time.time() + 30
        }

    def cache_contains(self, mac_address):
        if mac_address in self.mac_table:
            info = mac_address[mac_address]
            if info['type'] == 'static' or time.time() <= info['time_stamp']:
                return True
            else:
                self.mac_table.pop(mac_address)
        return False

    def clean_cache(self):
        for mac_address in self.mac_table.copy():
            info = self.mac_table[mac_address]
            if info['type'] == 'dynamic' and time.time() > info['time_stamp']:
                self.mac_address.pop(mac_address)


class Router:

    def __init__(self, *interfaces, **kwargs):
        self.extend = dict()
        self.interfaces = list(interfaces)
        for interface in interfaces:
            interface.attach_device(self)
            interface.attachment = self.__receive
            interface.params = [interface]

        self.arp_table = kwargs.get('arp_table') or dict()
        self.routing_table = kwargs.get('routing_table') or dict()
        self.name = kwargs.get('name')
        self.neighbors = dict()
        self.__buffer = set()

    def set_routing_table(self, info):
        self.routing_table = {
            ipa.ip_network(sub['destination']): {
                'next_hop': sub['next_hop'],
                'interface': self.get_interface_by_ip(sub['interface']),
                'type': sub['type']
            } for sub in info
        }

    def activate_rip(self, canvas):
        self.extend['RIP'] = {
            'hello_thread': None,
            'table': {
                interface.ip_network: {
                    'ip_network': interface.ip_network,
                    'via': None,
                    'hop': 0,
                } for interface in self.interfaces
            }
        }
        self.extend['RIP']['hello_thread'] = Thread(target=self.__hello, args=(canvas,))
        self.extend['RIP']['advertise_thread'] = Thread(target=self.__advertise, args=(canvas,))
        self.extend['RIP']['hello_thread'].start()
        self.extend['RIP']['advertise_thread'].start()

    def __hello(self, canvas):
        from random import uniform
        time.sleep(uniform(1, 10))
        while True and not self.__getattribute__('is_destroyed'):
            try:
                if not self.__getattribute__('active'):
                    time.sleep(1)
                    continue
            except AttributeError:
                pass
            for interface in self.interfaces:
                if hasattr(self, 'is_destroyed'):
                    if self.is_destroyed:
                        return
                hello_frame = data.Hello(interface.ip_address).build(interface.mac_address)
                interface.send(hello_frame, canvas)
            time.sleep(20)

    def __advertise(self, canvas):
        from random import uniform
        time.sleep(uniform(1, 10))
        while True and not self.__getattribute__('is_destroyed'):
            try:
                if not self.__getattribute__('active'):
                    time.sleep(1)
                    continue
            except AttributeError:
                pass
            for key, neighbor in self.neighbors.copy().items():
                if hasattr(self, 'is_destroyed'):
                    if self.is_destroyed:
                        return

                ip_address = neighbor['ip_address']
                mac_address = neighbor['mac_address']
                via = neighbor['via']
                if time.time() - neighbor['last_time'] > 20:
                    for rule in self.extend['RIP']['table'].copy().values():
                        if rule['via'] == ip_address:
                            rule['hop'] = float("inf")
                    self.neighbors.pop(key)
                    continue
                frame = data.RIP(via.ip_address,
                                 ip_address,
                                 self.extend['RIP']['table']).build(via.mac_address, mac_address)
                via.send(frame, canvas)
            time.sleep(20)

    """
    def set_routing_table(self, routing_table):
        self.routing_table = {
            ipa.ip_network(key): value for key, value in routing_table.items()
        }
    """

    def cache_arp(self, frame, receiver):
        packet = frame.packet
        if packet:
            if receiver.mac_address == frame.mac_target:
                if self.arp_table.get(receiver) is None:
                    self.arp_table[receiver] = dict()
                self.arp_table[receiver][packet.ip_source] = frame.mac_source

    def __receive(self, source, frame, canvas, receiver):
        try:
            if not self.__getattribute__('active'):
                return
        except AttributeError:
            pass
        # print(self.name, 'update arp table')
        self.cache_arp(frame, receiver)
        if ph.interface_arp_handler(receiver, frame, source=source, canvas=canvas):
            return
        if ph.router_hello_handler(self, frame, canvas=canvas, receiver=receiver):
            return
        if self.extend.get('RIP') and ph.router_rip_handler(self, frame, receiver=receiver):
            return
        ph.router_forward_handler(self, frame, source=source, receiver=receiver, canvas=canvas)

    def send(self, interface, frame, canvas=None):
        try:
            if not self.__getattribute__('active'):
                return
        except AttributeError:
            pass
        pass

    def forward(self, interface, frame, rule, canvas=None, init=True):
        try:
            if not self.__getattribute__('active'):
                return
        except AttributeError:
            pass
        if not init:
            buffer = (id(interface), id(frame), id(rule))
            if buffer not in self.__buffer:
                return
            else:
                self.__buffer.remove(buffer)
        packet = frame.packet
        if packet:
            next_hop = ipa.ip_address(rule['next_hop'])
            if self.arp_table.get(interface) and packet.ip_target in self.arp_table[interface]:
                forward_frame = data.Frame(
                    interface.mac_address,
                    self.arp_table[interface][frame.packet.ip_target],
                    packet)
                interface.send(forward_frame, canvas)
            elif packet.ip_target in interface.ip_network:
                self.__buffer.add((id(interface), id(frame), id(rule)))
                function = partial(self.forward, interface, frame, rule, canvas, False)
                arp = data.ARP(interface.ip_address, packet.ip_target, function)
                arp_frame = data.BroadcastFrame(interface.mac_address, arp)
                interface.send(arp_frame, canvas)
            elif self.arp_table.get(interface) and next_hop in self.arp_table[interface]:
                forward_frame = data.Frame(interface.mac_address, self.arp_table[interface][next_hop], packet)
                interface.send(forward_frame, canvas)
            else:
                self.__buffer.add((id(interface), id(frame), id(rule)))
                function = partial(self.forward, interface, frame, rule, canvas, False)
                arp = data.ARP(interface.ip_address, next_hop, function)
                arp_frame = data.BroadcastFrame(interface.mac_address, arp)
                interface.send(arp_frame, canvas)

    def add_interface(self, interface_info):
        interface = Interface(**interface_info)
        self.interfaces.append(interface)
        interface.attach_device(self)
        interface.attachment = self.__receive
        interface.params = [interface]

    def get_interface(self, name):
        for interface in self.interfaces:
            if interface.name == name:
                return interface

    def get_interface_by_ip(self, ip):
        ip = ipa.ip_address(ip)
        for interface in self.interfaces:
            if interface.ip_address == ip:
                return interface

    def json(self):
        result = {
            'type': 'router',
            'name': self.name,
            'interfaces': [
                interface.json() for interface in self.interfaces
            ],
            'routing_table': [
                {
                    'destination': str(key),
                    'next_hop': str(value['next_hop']),
                    'interface': str(value['interface'].ip_address),
                    'type': value['type']
                }
                for key, value in self.routing_table.items()
            ],
        }
        return result
