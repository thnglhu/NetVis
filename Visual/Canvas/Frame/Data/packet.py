from Resource import get_image

class Packet:
    def __init__(self, source, destination, segment):
        self.source = source
        self.destination = destination
        self.segment = segment

    @staticmethod
    def get_image():
        return get_image("mail")

    def get_name(self):
        return "Unknow"
