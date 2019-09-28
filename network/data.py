import ipaddress as ipa


class ARP:
    def __init__(self, source, target, func=None):
        self.source = source
        self.target = target
        self.func = func

    def print(self):
        print(self.source, self.target)

    def reply(self):
        return ARP(self.target, self.source, self.func)


class Segment:
    def __init__(self, data=None):
        self.data = data


class Packet:
    def __init__(self, source, target, segment):
        self.source = source
        self.target = target
        self.segment = segment

    def print(self):
        print(self.source, self.target)


class Frame:
    def __init__(self, source, target, packet):
        self.source = source
        self.target = target
        self.packet = packet

    def print(self):
        print(self.source, self.target)
        self.packet.print()


class BroadcastFrame(Frame):
    def __init__(self, source, packet):
        super().__init__(source, None, packet)
