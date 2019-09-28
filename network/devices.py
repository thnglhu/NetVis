import ipaddress as ipa
import data


class Interface:
    def __init__(self, **kwargs):
        self.switch = None
        self.attachment = None
        self.params = list()
        for att in kwargs:
            setattr(self, str(att), kwargs[att])

    def connect(self, device):
        if self.switch is not None:
            self.switch.unsubscribe(self)
        self.switch = device
        device.subscribe(self)

    def receive(self, source, frame):
        self.attachment(source, frame, *self.params)


class PC:
    def __init__(self, interface, **kwargs):
        self.interface = interface
        interface.attachment = self.__receive
        self.arp_table = kwargs.get('arp_table') or dict()
        self.name = kwargs.get('name')

    def send(self, segment, target):
        print("<%s>" % self.name, 'send to', target)
        source = self.interface.ip_address
        packet = data.Packet(source, target, segment)
        mac_source = self.interface.mac_address
        if target not in self.interface.ip_network:
            print(target, end='')
            target = self.interface.default_gateway

        def func():
            if target in self.arp_table:
                mac_target = self.arp_table[target]
                frame = data.Frame(mac_source, mac_target, packet)
                print('send frame')
                self.interface.switch.receive(self, frame)
            else:
                arp = data.ARP(self.interface.ip_address, target, func)
                frame = data.BroadcastFrame(self.interface.mac_address, arp)
                print('send arp')
                self.interface.switch.receive(self.interface, frame)
        func()

    def __receive(self, source, frame):
        print("<%s>" % self.name, 'receive from', source.name)
        packet = frame.packet
        if isinstance(frame, data.BroadcastFrame):
            if isinstance(packet, data.ARP):
                if packet.target == self.interface.ip_address:
                    reply = packet.reply()
                    frame = data.Frame(self.interface.mac_address, frame.source, reply)
                    source.receive(self.interface, frame)
                else:
                    print('Drop due to unmatched ip address', packet.target, self.interface.ip_address)
        else:
            if frame.target == self.interface.mac_address:
                if isinstance(packet, data.ARP):
                    if packet.target == self.interface.ip_address:
                        self.arp_table[packet.source] = frame.source
                        packet.func()
                elif isinstance(packet, data.Packet):
                    if packet.target == self.interface.ip_address:
                        print('Receive', "\"%s\"" % packet.segment)


class Switch:
    def __init__(self, **kwargs):
        self.mac_table = kwargs.get('mac_table') or dict()
        self.interfaces = list()
        self.name = kwargs.get('name')

    def subscribe(self, interface):
        self.interfaces.append(interface)

    def unsubscribe(self, interface):
        if interface not in self.interfaces:
            raise IndexError
        self.interfaces.pop(interface)
        for _mac in self.mac_table:
            if interface is self.mac_table[_mac]:
                self.mac_table.pop(_mac)
                break

    def receive(self, source, frame):
        print("<%s>" % self.name, 'receive from', source.name)
        self.mac_table[frame.source] = source
        if frame.target in self.mac_table:
            self.mac_table[frame.target].receive(self, frame)
        elif frame.target is None:
            for interface in self.interfaces:
                if interface is not source:
                    print(interface.name)
                    interface.receive(self, frame)


class Router:
    """
    def __init__(self, *interfaces, **kwargs):
        self.interfaces = interfaces
        self.arp_table = kwargs.get('arp_table') or dict()
        self.mac_table = kwargs.get('mac_table') or dict()
    """
    def __init__(self, *interfaces, **kwargs):
        self.interfaces = interfaces
        for index, interface in enumerate(interfaces):
            interface.attachment = self.__receive
            interface.params = [interface]
            print(interface.receive)
        self.arp_table = kwargs.get('arp_table') or dict()
        self.routing_table = kwargs.get('routing_table') or dict()
        self.name = kwargs.get('name')

    def __receive(self, source, frame, interface):
        print("<%s>" % self.name, 'receive from', source.name, 'interface:', interface.name)
        packet = frame.packet
        if isinstance(frame, data.BroadcastFrame):
            if isinstance(packet, data.ARP):
                if packet.target == interface.ip_address:
                    reply = packet.reply()
                    frame = data.Frame(interface.mac_address, frame.source, reply)
                    source.receive(interface, frame)
                else:
                    print('Drop due to unmatched ip address', packet.target, interface.ip_address)
        else:
            if frame.target == interface.mac_address:
                if isinstance(packet, data.ARP):
                    if packet.target is interface.ip_address:
                        self.arp_table[packet.source] = frame.source
                        packet.func()
                elif isinstance(packet, data.Packet):
                    def func():
                        for forward_interface in self.interfaces:
                            if packet.target in forward_interface.ip_network:
                                if forward_interface.switch:
                                    if packet.target in self.arp_table:
                                        print('send frame')
                                        forward_frame = data.Frame(forward_interface.mac_address, self.arp_table[packet.target], packet)
                                        forward_interface.switch.receive(forward_interface, forward_frame)
                                    else:
                                        print('send arp')
                                        arp = data.ARP(forward_interface.ip_address, packet.target, func)
                                        forward_frame = data.BroadcastFrame(forward_interface.mac_address, arp)
                                        forward_interface.switch.receive(forward_interface, forward_frame)
                                break
                        else:
                            print('Drop')
                    func()
            else:
                print('Drop due to unmatched mac address: ', frame.target, interface.mac_address)


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
    routing_table = {
        ipa.ip_network('192.168.0.0/24'): interface0,
        ipa.ip_network('10.10.0.0/24'): iterface20
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

    pc1 = PC(i1, name='A')
    pc2 = PC(i2, name='B')
    pc21 = PC(i21, name='C')
    pc22 = PC(i22, name='D')
    switch = Switch(name='switch 0')
    switch2 = Switch(name='switch 1')
    router = Router(i0, i20, name='router', routing_table=routing_table)
    i0.connect(switch)
    i1.connect(switch)
    i2.connect(switch)
    i20.connect(switch2)
    i21.connect(switch2)
    i22.connect(switch2)
    # print(pc1, pc2, switch, i1, i2, sep='\n')
    # pc1.send(None, ipa.ip_address('192.168.0.3'))
    pc1.send("pc1 wanna say hi", ipa.ip_address('10.10.0.3'))
