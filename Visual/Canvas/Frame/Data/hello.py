from .packet import Packet
from Resource import get_image


class Hello(Packet):

    def __init__(self, source, destination=None, request=True):
        super().__init__(source, destination, None)
        self.request = request

    def get_image(self):
        return get_image("hello") if self.request else get_image("hello-reply")

    def get_name(self):
        return "hello"
