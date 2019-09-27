import ipaddress as ipa
# from . import data
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
        else:
            raise NotImplementedError
        frame = data.Frame(mac_source, mac_target, packet)
        self.interface['switch'].receive(frame)

    def receive(self, frame):
        print(self, frame)

    def connect(self, switch):
        if 'switch' in self.interface:
            self.interface['switch'].unsubscribe()
        switch.subscribe(self)
        self.interface['switch'] = switch


class Switch:
    def __init__(self):
        self.mac_table = dict()
        self.devices = list()

    def subscribe(self, device):
        self.devices.append(device)
        """
        test only
        """
        self.mac_table[device.interface['mac_address']] = device

    def unsubscribe(self, device):
        if device not in self.devices:
            raise IndexError
        self.devices.pop(device)
        for _mac in self.mac_table:
            if device is self.mac_table[_mac]:
                self.mac_table.pop(_mac)
                break

    def receive(self, data):
        if data.target in self.mac_table:
            print('forward')
            self.mac_table[data.target].receive(data)


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
    pc1 = PC(interface1, arp_table=arp_table1)
    pc2 = PC(interface2, arp_table=arp_table2)
    switch = Switch()
    router = Router(interface0, arp_table=arp_table0)
    pc1.connect(switch)
    pc2.connect(switch)
    pc1.send(None, ipa.ip_address('192.168.0.3'))

