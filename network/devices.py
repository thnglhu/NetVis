import ipaddress as ipa
import data


class PC:
    def __init__(self, interface, **kwargs):
        self.interface = interface
        self.arp_table = kwargs.get('arp_table') or dict()

    def send(self, segment, target):
        source = self.interface['ip_address']
        packet = data.Packet(source, target, segment)
        mac_source = self.interface['mac_address']
        if target not in self.interface.get('ip_network'):
            target = self.interface.get('default_gateway')
        if target in self.arp_table:
            mac_target = self.arp_table[target]
            frame = data.Frame(mac_source, mac_target, packet)
            self.interface['switch'].receive(self, frame)
        else:
            def func():
                self.send(segment, target)
            arp = data.ARP(self.interface['ip_address'], target, func)
            frame = data.BroadcastFrame(self.interface['mac_address'], arp)
            self.interface['switch'].receive(self, frame)

    def receive(self, source, frame):
        packet = frame.packet
        if isinstance(frame, data.BroadcastFrame):
            if isinstance(packet, data.ARP):
                if packet.target == self.interface['ip_address']:
                    reply = packet.reply()
                    frame = data.Frame(self.interface['mac_address'], frame.source, reply)
                    source.receive(self, frame)
                else:
                    print('Drop', frame)
        else:
            if isinstance(packet, data.ARP):
                if packet.target is self.interface['ip_address']:
                    self.arp_table[packet.source] = frame.source
                    packet.func()

    def connect(self, device):
        if 'switch' in self.interface:
            self.interface['switch'].unsubscribe()
        device.subscribe(self)
        self.interface['switch'] = device


class Switch:
    def __init__(self, **kwargs):
        self.mac_table = kwargs.get('mac_table') or dict()
        self.devices = list()

    def subscribe(self, device):
        self.devices.append(device)

    def unsubscribe(self, device):
        if device not in self.devices:
            raise IndexError
        self.devices.pop(device)
        for _mac in self.mac_table:
            if device is self.mac_table[_mac]:
                self.mac_table.pop(_mac)
                break

    def receive(self, source, frame):
        self.mac_table[frame.source] = source
        if frame.target in self.mac_table:
            self.mac_table[frame.target].receive(self, frame)
        elif frame.target is None:
            for device in self.devices:
                if device is not source:
                    device.receive(self, frame)


class Router:
    def __init__(self, *interfaces, **kwargs):
        self.interfaces = interfaces
        self.arp_table = kwargs.get('arp_table') or dict()
        self.mac_table = kwargs.get('mac_table') or dict()


if __name__ == '__main__':
    interface0 = {
        'ip_address': ipa.ip_address('192.168.0.1'),
        'ip_network': ipa.ip_network('192.168.0.0/24'),
        'mac_address': 'aa.aa.aa.aa.aa.aa',
    }
    interface1 = {
        'ip_address': ipa.ip_address('192.168.0.2'),
        'ip_network': ipa.ip_network('192.168.0.0/24'),
        'mac_address': 'aa.aa.aa.aa.aa.bb',
        'default_gateway': ipa.ip_address('192.168.0.1')
    }
    interface2 = {
        'ip_address': ipa.ip_address('192.168.0.3'),
        'ip_network': ipa.ip_network('192.168.0.0/24'),
        'mac_address': 'aa.aa.aa.aa.aa.cc',
        'default_gateway': ipa.ip_address('192.168.0.1')
    }
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
    pc1 = PC(interface1)
    pc2 = PC(interface2)
    switch = Switch()
    router = Router(interface0)
    pc1.connect(switch)
    pc2.connect(switch)
    print(pc1.arp_table)
    print(pc2.arp_table)
    print(switch.devices)
    print(switch.mac_table)
    pc1.send(None, ipa.ip_address('192.168.0.3'))
    print(pc1.arp_table)
    print(pc2.arp_table)
    print(switch.devices)
    print(switch.mac_table)
