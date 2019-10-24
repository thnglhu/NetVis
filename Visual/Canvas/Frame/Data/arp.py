from .packet import Packet
from Resource import get_image


class ARP(Packet):

    def __init__(self, source, destination, request=True):
        super().__init__(source, destination, None)
        self.request = request

    def get_image(self):
        return get_image("arp") if self.request else get_image("arp-reply")

    def get_name(self):
        return "arp"