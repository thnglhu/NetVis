import ipaddress as ipa
from . import data
from visual import vnetwork as vn


class Interface:
    device = None
    name = 'unknown'

    def __init__(self, **kwargs):
        self.other = None
        self.attachment = None
        self.params = []
        for att in kwargs:
            setattr(self, str(att), kwargs[att])

    def info(self):
        return {
            'ip_address': self.ip_address,
            'ip_network': self.ip_network,
            'default_gateway': self.__getattribute__('default_gateway')
        }

    def modify(self, info):
        self.ip_address = ipa.ip_address(info['ip_address'])
        self.ip_network = ipa.ip_network(info['ip_network'])
        self.default_gateway = info['default_gateway']

    def connect(self, other):
        self.other = other
        other.attach(self)

    def attach(self, other):
        self.other = other

    def attach_device(self, device):
        self.device = device

    def receive(self, source, frame, canvas=None):
        if isinstance(frame, data.BroadcastFrame) or frame.mac_target == self.mac_address:
            self.attachment(source, frame, canvas, *self.params)
        else:
            print('drop at', self.name)

    def send(self, frame, canvas=None):
        if self.other is None:
            print('Connection is not available')
            return
        if canvas:
            my_device = self.device
            other_device = self.other.device
            edges = my_device.link_edges.intersection(other_device.link_edges)
            for edge in edges:
                is_inverted = not edge.points[0] == my_device
                if isinstance(frame.packet, data.ARP):
                    color = 'red'
                else:
                    color = 'blue'
                f = vn.Frame(edge, self.other.receive, (self, frame, canvas), is_inverted, fill=color)
                f.display(canvas)
                f.start_animation()
        else:
            self.other.receive(self, frame, canvas)


class Host:
    def __init__(self, interface, **kwargs):
        if isinstance(interface, dict):
            interface = Interface(**interface)
        self.interface = interface
        interface.attach_device(self)
        interface.attachment = self.__receive
        self.arp_table = kwargs.get('arp_table') or dict()
        self.name = kwargs.get('name')

    def send(self, canvas, ip_target, segment=None):
        if not self.interface:
            print('No connection')
            return

        def function():
            if ip_target in self.arp_table:
                packet = data.Packet(self.interface.ip_address, ip_target, segment)
                frame = data.Frame(self.interface.mac_address, self.arp_table[ip_target], packet)
            elif ip_target in self.interface.ip_network:
                packet = data.ARP(self.interface.ip_address, ip_target, function)
                frame = data.BroadcastFrame(self.interface.mac_address, packet)
            elif self.interface.default_gateway in self.arp_table:
                packet = data.Packet(self.interface.ip_address, ip_target, segment)
                frame = data.Frame(self.interface.mac_address, self.arp_table[self.interface.default_gateway], packet)
            else:
                print(self.name, 'is looking for the default gateway', self.interface.default_gateway)
                packet = data.ARP(self.interface.ip_address, self.interface.default_gateway, function)
                frame = data.BroadcastFrame(self.interface.mac_address, packet)
            self.interface.send(frame, canvas)
        function()

    def __receive(self, source, frame, canvas=None):
        self.arp_table[frame.packet.ip_source] = frame.mac_source
        # print(self.name, 'update arp table')
        if frame.packet.ip_target == self.interface.ip_address:
            if isinstance(frame.packet, data.ARP):
                if frame.packet.is_reply:
                    # print('Mac address of %s is %s' % (frame.packet.ip_source, frame.mac_source))
                    frame.packet.func()
                else:
                    reply_arp = frame.packet.reply()
                    frame = data.Frame(self.interface.mac_address, frame.mac_source, reply_arp)
                    self.interface.send(frame, canvas)
            else:
                print('receive something')


class Hub:
    def __init__(self, **kwargs):
        self.device = self
        self.name = kwargs.get('name')
        self.others = set()

    def attach(self, other):
        self.others.add(other)

    def receive(self, source, frame, canvas=None):
        for other in self.others:
            if other is not source:
                self.send(frame, other, canvas)

    def send(self, frame, target, canvas=None):
        if target is None:
            print('Connection is not available')
            return
        if canvas:
            my_device = self.device
            other_device = target.device
            edges = my_device.__getattribute__('link_edges').intersection(other_device.link_edges)
            for edge in edges:
                is_inverted = not edge.points[0] == my_device
                color = 'red' if isinstance(frame.packet, data.ARP) else 'blue'
                f = vn.Frame(edge, target.receive, (self, frame, canvas), is_inverted, fill=color)
                f.display(canvas)
                f.start_animation()
        else:
            target.receive(self, frame, canvas)


class Switch(Hub):
    def __init__(self, **kwargs):
        self.mac_table = kwargs.get('mac_table') or dict()
        self.others = set()
        super().__init__(**kwargs)

    def receive(self, source, frame, canvas=None):
        # print(self.name, 'update mac table')
        self.mac_table[frame.mac_source] = source
        if isinstance(frame, data.BroadcastFrame):
            super().receive(source, frame, canvas)
        else:
            if frame.mac_target in self.mac_table:
                # print(self.name, frame.mac_target, 'is cached')
                self.send(frame, self.mac_table[frame.mac_target], canvas)


class Router:
    def __init__(self, *interfaces, **kwargs):
        self.interfaces = interfaces
        for interface in interfaces:
            interface.attach_device(self)
            interface.attachment = self.__receive
            interface.params = [interface]

        self.arp_table = kwargs.get('arp_table') or dict()
        self.routing_table = kwargs.get('routing_table') or dict()
        self.name = kwargs.get('name')

    def __receive(self, source, frame, canvas, receiver):
        # print(self.name, 'update arp table')
        self.arp_table[frame.packet.ip_source] = frame.mac_source
        if frame.packet.ip_target == receiver.ip_address:
            if isinstance(frame.packet, data.ARP):
                if frame.packet.is_reply:
                    # print(self.name, 'mac address of %s is %s' % (frame.packet.ip_source, frame.mac_source))
                    frame.packet.func()
                else:
                    reply_arp = frame.packet.reply()
                    frame = data.Frame(receiver.mac_address, frame.mac_source, reply_arp)
                    receiver.send(frame, canvas)
            else:
                print('receive something')
        else:
            if isinstance(frame.packet, data.ARP):
                return
            for network in self.routing_table:
                if frame.packet.ip_target in network:
                    if frame.packet.ip_target == self.routing_table[network].ip_address:
                        print('receive something')
                    else:
                        self.send(self.routing_table[network], frame, canvas)
                    break
            else:
                print('drop')

    def send(self, interface, frame, canvas=None):
        if interface.other is None:
            print("Connection is not avaiable")
            return

        def func():
            if frame.packet.ip_target in self.arp_table:
                # print(self.name, frame.packet.ip_target, 'is cached')
                next_frame = data.Frame(interface.mac_address, self.arp_table[frame.packet.ip_target], frame.packet)
            else:
                # print(self.name, 'is looking for', frame.packet.ip_target)
                packet = data.ARP(interface.ip_address, frame.packet.ip_target, func)
                next_frame = data.BroadcastFrame(interface.mac_address, packet)
            interface.send(next_frame, canvas)
        func()


if __name__ == '__main__':
    pass
    # print(pc1, pc2, switch, i1, i2, sep='\n')
    # pc1.send(None, ipa.ip_address('192.168.0.3'))
    # pc1.send("pc1 wanna say hi", ipa.ip_address('10.10.0.3'))

