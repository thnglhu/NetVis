from Resource import get_image


class Frame:
    def __init__(self, source, destination, packet):
        self.source = source
        self.destination = destination
        self.packet = packet

    def get_image(self):
        if self.packet:
            return self.packet.get_image()
        return get_image("mail")

    def get_name(self):
        if self.packet:
            return self.packet.get_name()
        return "Unknown"

