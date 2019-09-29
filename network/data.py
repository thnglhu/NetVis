import ipaddress as ipa


class Segment:
    def __init__(self, data=None):
        self.data = data


class Packet:
    def __init__(self, source, target, segment=None, func=None):
        self.ip_source = source
        self.ip_target = target
        self.segment = segment
        self.func = func

    def print(self):
        print(self.ip_source, self.ip_target)


class ARP(Packet):
    def __init__(self, source, target, func=None):
        super().__init__(source, target, None, func)
        self.is_reply = False

    def print(self):
        print(self.ip_source, self.ip_target)

    def reply(self):
        reply_arp = ARP(self.ip_target, self.ip_source, self.func)
        reply_arp.is_reply = True
        return reply_arp


class Frame:
    def __init__(self, source, target, packet):
        self.mac_source = source
        self.mac_target = target
        self.packet = packet

    def print(self):
        print(self.mac_source, self.mac_target)
        self.packet.print()


class BroadcastFrame(Frame):
    def __init__(self, source, packet):
        super().__init__(source, None, packet)

