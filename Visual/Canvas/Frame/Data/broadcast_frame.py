from .frame import Frame


class BroadcastFrame(Frame):
    def __init__(self, source, packet):
        super().__init__(source, "FF:FF:FF:FF:FF:FF", packet)