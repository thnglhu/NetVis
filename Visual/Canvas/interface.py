from ipaddress import ip_interface as ipi, ip_address as ipa
from .port import Port
from .Frame.Data import ARP, BroadcastFrame, Frame
from time import time


class Interface:

    # region Declaration
    def __init__(self, info, device):
        self.device = device
        self.mac_address = info['mac_address']
        self.ip_interface = ipi(info['ip_interface'])
        self.port = Port(info['port']['name'], self, info['port'].get('id'))
        self.buffer = set()
        self.arp_table = dict()

    def __getattr__(self, item):
        return getattr(self.device, item)

    def info(self):
        return {
            'name': self.port.name,
            'mac_address': self.mac_address,
            'ip_interface': self.ip_interface,
            'default_gateway': self.default_gateway,
        }

    def subscribe(self, link):
        self.device.subscribe(link)

    def unsubscribe(self, link):
        self.device.unsubscribe(link)

    def destroy(self, collector):
        self.port.destroy(collector)

    def save(self):
        return {
            'mac_address': self.mac_address,
            'ip_interface': str(self.ip_interface),
            'port': self.port.save(),
        }

    def modify(self, info):
        self.mac_address = info['mac_address']
        self.ip_interface = ipi(info['ip_interface'])
        self.port.name = info['port']['name']
    # endregion

    # region Logical
    def disconnect(self, _):
        pass

    def send(self, packet, alternative=None):
        if packet.destination not in self.ip_interface.network:
            if alternative and ipa(alternative) in self.ip_interface.network:
                if alternative in self.arp_table:
                    frame = Frame(self.mac_address, self.arp_table[alternative]['mac_address'], packet)
                    self.port.send(frame)
                else:
                    self.buffer.add(("ARP", packet, alternative))
                    arp_request = ARP(self.ip_interface.ip, alternative)
                    arp_frame = BroadcastFrame(self.mac_address, arp_request)
                    self.port.send(arp_frame)
            return
        if str(packet.destination) in self.arp_table:
            frame = Frame(self.mac_address, self.arp_table[str(packet.destination)]['mac_address'], packet)
            self.port.send(frame)
        else:
            self.buffer.add(("ARP", packet))
            arp_request = ARP(self.ip_interface.ip, packet.destination)
            arp_frame = BroadcastFrame(self.mac_address, arp_request)
            self.port.send(arp_frame)

    def broadcast(self, packet):
        frame = BroadcastFrame(self.mac_address, packet)
        self.port.send(frame)

    def receive(self, frame, port):
        if frame.destination == self.mac_address or isinstance(frame, BroadcastFrame):
            if frame.packet:
                if ipa(frame.packet.source) in self.ip_interface.network:
                    self.arp_table[str(frame.packet.source)] = {
                        'mac_address': frame.source,
                        'time': time(),
                    }
                    self.update()
                if isinstance(frame.packet, ARP):
                    if frame.packet.request:
                        if str(frame.packet.destination) == str(self.ip_interface.ip):
                            arp_reply = ARP(self.ip_interface.ip, frame.source, False)
                            arp_frame = Frame(self.mac_address, frame.source, arp_reply)
                            self.port.send(arp_frame)
                        else:
                            return False
                    else:
                        for each in self.buffer.copy():
                            if each[0] == "ARP" and \
                                    ((len(each) == 2 and str(each[1].destination) == str(frame.packet.source))
                                     or (len(each) == 3 and str(each[2]) == str(frame.packet.source))):
                                try:
                                    self.buffer.remove(each)
                                    self.send(*each[1:])
                                except KeyError:
                                    pass
                    return True
            return self.device.receive(frame, port)
        return False
    # endregion
