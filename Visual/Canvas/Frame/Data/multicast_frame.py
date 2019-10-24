from .frame import Frame


class MulticastFrame(Frame):
    def __init__(self, source, destination, packet):
        super().__init__(source, destination, packet)
