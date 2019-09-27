import ipaddress as ipa


class ARP:
    def __init__(self, source, target, request=True, func=None):
        self.source = source
        self.target = target
        self.request = request
        self.func = func


class Segment:
    def __init__(self, data=None):
        self.data = data


class Packet:
    def __init__(self, source, target, segment):
        self.source = source
        self.target = target
        self.segment = segment


class Frame:
    def __init__(self, source, target, packet):
        self.source = source
        self.target = target
        self.segment = packet
