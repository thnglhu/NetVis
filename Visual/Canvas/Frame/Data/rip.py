from .packet import Packet
from Resource import get_image


class RIP(Packet):

    def __init__(self, source, destination, info):
        super().__init__(source, destination, None)
        self.info = [
            {
                'network': str(key),
                'hop': value['hop'] if not value['hop'] == float('inf') else 'inf',
                'via': str(value['via'])
            } for key, value in info.items()
        ]

    def get_image(self):
        return get_image("rip")

    def get_name(self):
        return "rip"
