import ipaddress as ipa
import data


class Interface:
    def __init__(self, **kwargs):
        self.other = None
        self.attachment = None
        self.params = []
        for att in kwargs:
            setattr(self, str(att), kwargs[att])

    def connect(self, other):
        self.other = other
        other.attach(self)

    def attach(self, other):
        self.other = other

    def receive(self, source, frame):
        print('%s receives from %s' % (self.name, self.other.name))
        if isinstance(frame, data.BroadcastFrame) or frame.mac_target == self.mac_address:
            self.attachment(source, frame, *self.params)
        else:
            print('drop at', self.name)

    def send(self, frame):
        print('%s sends to %s' % (self.name, self.other.name))
        self.other.receive(self, frame)


class Host:
    def __init__(self, interface, **kwargs):
        self.interface = interface
        interface.attachment = self.__receive
        self.arp_table = kwargs.get('arp_table') or dict()
        self.name = kwargs.get('name')

    def send(self, info, ip_target):
        def function():
            if ip_target in self.arp_table:
                packet = data.Packet(self.interface.ip_address, ip_target)
                frame = data.Frame(self.interface.mac_address, self.arp_table[ip_target], packet)
            elif ip_target in self.interface.ip_network:
                packet = data.ARP(self.interface.ip_address, ip_target, function)
                frame = data.BroadcastFrame(self.interface.mac_address, packet)
            elif self.interface.default_gateway in self.arp_table:
                packet = data.Packet(self.interface.ip_address, ip_target)
                frame = data.Frame(self.interface.mac_address, self.arp_table[self.interface.default_gateway], packet)
            else:
                packet = data.ARP(self.interface.ip_address, self.interface.default_gateway, function)
                frame = data.BroadcastFrame(self.interface.mac_address, packet)
            self.interface.send(frame)
        function()

    def __receive(self, source, frame):
        self.arp_table[frame.packet.ip_source] = frame.mac_source
        if frame.packet.ip_target == self.interface.ip_address:
            if isinstance(frame.packet, data.ARP):
                if frame.packet.is_reply:
                    # print('Mac address of %s is %s' % (frame.packet.ip_source, frame.mac_source))
                    frame.packet.func()
                else:
                    reply_arp = frame.packet.reply()
                    frame = data.Frame(self.interface.mac_address, frame.mac_source, reply_arp)
                    self.interface.send(frame)
            else:
                print('receive something')


class Hub:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.others = set()

    def attach(self, other):
        self.others.add(other)

    def receive(self, source, frame):
        for other in self.others:
            if other is not source:
                self.send(frame, other)

    def send(self, frame, target):
        print('%s sends to %s' % (self.name, target.name))
        target.receive(self, frame)


class Switch(Hub):
    def __init__(self, **kwargs):
        self.mac_table = kwargs.get('mac_table') or dict()
        self.others = set()
        super().__init__(**kwargs)

    def receive(self, source, frame):
        self.mac_table[frame.mac_source] = source
        if isinstance(frame, data.BroadcastFrame):
            super().receive(source, frame)
        else:
            if frame.mac_target in self.mac_table:
                self.send(frame, self.mac_table[frame.mac_target])


class Router:
    def __init__(self, *interfaces, **kwargs):
        self.interfaces = interfaces
        for interface in interfaces:
            interface.attachment = self.__receive
            interface.params = [interface]

        self.arp_table = kwargs.get('arp_table') or dict()
        self.routing_table = kwargs.get('routing_table') or dict()
        self.name = kwargs.get('name')

    def __receive(self, source, frame, receiver):
        self.arp_table[frame.packet.ip_source] = frame.mac_source
        if frame.packet.ip_target == receiver.ip_address:
            if isinstance(frame.packet, data.ARP):
                if frame.packet.is_reply:
                    print(self.name)
                    print('Mac address of %s is %s' % (frame.packet.ip_source, frame.mac_source))
                    frame.packet.func()
                else:
                    reply_arp = frame.packet.reply()
                    frame = data.Frame(receiver.mac_address, frame.mac_source, reply_arp)
                    receiver.send(frame)
            else:
                print('receive something')
        else:
            if isinstance(frame.packet, data.ARP):
                return
            for network in self.routing_table:
                if frame.packet.ip_target in network:
                    self.send(self.routing_table[network], frame)
                    break
            else:
                print('drop')

    def send(self, interface, frame):
        def func():
            if frame.packet.ip_target in self.arp_table:
                next_frame = data.Frame(interface.mac_address, self.arp_table[frame.packet.ip_target], frame.packet)
            else:
                packet = data.ARP(interface.ip_address, frame.packet.ip_target, func)
                next_frame = data.BroadcastFrame(interface.mac_address, packet)
            interface.send(next_frame)
        func()


if __name__ == '__main__':
    interface0 = {
        'name': 'interface0',
        'ip_address': ipa.ip_address('192.168.0.1'),
        'ip_network': ipa.ip_network('192.168.0.0/24'),
        'mac_address': 'aa.aa.aa.aa.aa.aa',
    }
    interface1 = {
        'name': 'interface1',
        'ip_address': ipa.ip_address('192.168.0.2'),
        'ip_network': ipa.ip_network('192.168.0.0/24'),
        'mac_address': 'aa.aa.aa.aa.aa.bb',
        'default_gateway': ipa.ip_address('192.168.0.1')
    }
    interface2 = {
        'name': 'interface2',
        'ip_address': ipa.ip_address('192.168.0.3'),
        'ip_network': ipa.ip_network('192.168.0.0/24'),
        'mac_address': 'aa.aa.aa.aa.aa.cc',
        'default_gateway': ipa.ip_address('192.168.0.1')
    }
    interface20 = {
        'name': 'interface20',
        'ip_address': ipa.ip_address('10.10.0.1'),
        'ip_network': ipa.ip_network('10.10.0.0/24'),
        'mac_address': 'aa.aa.aa.aa.aa.00'
    }
    interface21 = {
        'name': 'interface21',
        'ip_address': ipa.ip_address('10.10.0.2'),
        'ip_network': ipa.ip_network('10.10.0.0/24'),
        'mac_address': 'aa.aa.aa.aa.aa.11',
        'default_gateway': ipa.ip_address('10.10.0.1')
    }
    interface22 = {
        'name': 'interface22',
        'ip_address': ipa.ip_address('10.10.0.3'),
        'ip_network': ipa.ip_network('10.10.0.0/24'),
        'mac_address': 'aa.aa.aa.aa.aa.22',
        'default_gateway': ipa.ip_address('10.10.0.1')
    }
    interface31 = {
        'name': 'interface31',
        'ip_address': ipa.ip_address('172.16.0.1'),
        'ip_network': ipa.ip_network('172.16.0.0/20')
    }
    interface32 = {
        'name': 'interface32',
        'ip_address': ipa.ip_address('172.16.0.2'),
        'ip_network': ipa.ip_network('172.16.0.0/20')
    }
    """
    arp_table0 = {
        ipa.ip_address('192.168.0.3'): 'aa.aa.aa.aa.aa.cc',
        ipa.ip_address('192.168.0.2'): 'aa.aa.aa.aa.aa.bb'
    }
    arp_table1 = {
        ipa.ip_address('192.168.0.3'): 'aa.aa.aa.aa.aa.cc',
        ipa.ip_address('192.168.0.1'): 'aa.aa.aa.aa.aa.aa'
    }
    arp_table2 = {
        ipa.ip_address('192.168.0.2'): 'aa.aa.aa.aa.aa.bb',
        ipa.ip_address('192.168.0.1'): 'aa.aa.aa.aa.aa.aa'
    }
    arp_table20 = {
        ipa.ip_address('192.168.0.3'): 'aa.aa.aa.aa.aa.cc',
        ipa.ip_address('192.168.0.2'): 'aa.aa.aa.aa.aa.bb'
    }
    arp_table21 = {
        ipa.ip_address('192.168.0.3'): 'aa.aa.aa.aa.aa.cc',
        ipa.ip_address('192.168.0.1'): 'aa.aa.aa.aa.aa.aa'
    }
    arp_table22 = {
        ipa.ip_address('192.168.0.2'): 'aa.aa.aa.aa.aa.bb',
        ipa.ip_address('192.168.0.1'): 'aa.aa.aa.aa.aa.aa'
    }"""
    i1 = Interface(**interface1)
    i2 = Interface(**interface2)
    i0 = Interface(**interface0)
    i21 = Interface(**interface21)
    i22 = Interface(**interface22)
    i20 = Interface(**interface20)

    routing_table = {
        ipa.ip_network('192.168.0.0/24'): i0,
        ipa.ip_network('10.10.0.0/24'): i20
    }

    pc1 = Host(i1, name='A')
    pc2 = Host(i2, name='B')
    pc21 = Host(i21, name='C')
    pc22 = Host(i22, name='D')
    switch = Switch(name='switch 0')
    switch2 = Switch(name='switch 1')
    router = Router(i0, i20, name='router', routing_table=routing_table)
    router2 = Router(i0, i20, name='router2', routing_table=routing_table2)
    i0.connect(switch)
    i1.connect(switch)
    i2.connect(switch)
    i20.connect(switch2)
    i21.connect(switch2)
    i22.connect(switch2)
    # print(pc1, pc2, switch, i1, i2, sep='\n')
    # pc1.send(None, ipa.ip_address('192.168.0.3'))
    pc1.send("pc1 wanna say hi", ipa.ip_address('10.10.0.3'))
