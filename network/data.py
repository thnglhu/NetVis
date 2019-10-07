import ipaddress as ipa
import resource

class Segment:
    def __init__(self, data=None):
        self.data = data
        self.size = 1

    def get_size(self):
        return self.size


class Packet:
    def __init__(self, source, target, segment=None, func=None):
        self.ip_source = source
        self.ip_target = target
        self.segment = segment
        self.func = func

    def print(self):
        print(self.ip_source, self.ip_target)

    def get_size(self):
        return self.segment.get_size() + 2

    def build(self, *args):
        return Frame(args[0], args[1], self)

    def get_image(self):
        return resource.get_image('mail')


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

    def get_size(self):
        return 28

    def build(self, *args):
        return BroadcastFrame(args[0], self)

    def get_image(self):
        return resource.get_image(
            'arp-reply' if self.is_reply
            else 'arp'
        )


class Frame:
    def __init__(self, source, target, packet):
        self.mac_source = source
        self.mac_target = target
        self.packet = packet

    def print(self):
        # print(self.mac_source, self.mac_target)
        self.packet.print()

    def get_size(self):
        return self.packet.get_size() + 16

    def build(self):
        return self


class BroadcastFrame(Frame):
    def __init__(self, source, packet):
        super().__init__(source, None, packet)


class ICMP(Packet):
    def __init__(self, source, target, last, segment=None, func=None):
        self.last = last
        self.route = [last]
        self.state = "echo"
        self.unreachable = False
        super().__init__(source, target, segment, func)

    def get_image(self):
        return resource.get_image(
            'icmp-unreachable' if self.unreachable
            else 'icmp' if self.state == "echo"
            else "icmp-reply")

    def reply(self):
        rep = ICMP(self.ip_target, self.ip_source, self.route[-1], self.segment, self.func)
        rep.state = "reply"
        return rep

    def get_size(self):
        return 74
