from .vertex import Vertex
from ..port import Port
from ..interface import Interface
from Resource import get_image


class Host(Vertex):

    # region Canvas declaration
    def __init__(self, canvas, info):
        super().__init__(canvas)
        self.position = info['position']
        self.name = info['name']
        self.default_gateway = info['default_gateway']
        self.interface = Interface(info['interface'], self)
        self.type = 'host'
        self.active = info['status']
        if not self.active:
            self.interface.port.disable()
        self['image'] = self['on-image'] if self.active else self['off-image']

    def _set_image(self):
        self['on-image'] = get_image('_pc-on')
        self['off-image'] = get_image('_pc-off')

    def get_ports(self):
        return {
            self.interface.port
        }

    def destroy(self, collector):
        super().destroy(collector)
        self.interface.destroy(collector)

    def save(self):
        return {
            'type': self.type,
            'status': self.active,
            'name': self.name,
            'default_gateway': self.default_gateway,
            'position': tuple(self.position),
            'interface': self.interface.save(),
        }

    def modify(self, info):
        self.name = info['name']
        self.default_gateway = info['default_gateway']
        self.interface.modify(info['interface'])
    # endregion

    # region GUI
    # endregion

    # region Logical
    def send(self, target):
        from ..Frame.Data.packet import Packet
        packet = Packet(self.interface.ip_interface.ip, target, None)
        self.interface.send(packet, self.default_gateway)

    def receive(self, frame, port):
        return True

    def enable(self):
        self.active = True
        self.interface.port.enable()
        self['image'].unsubscribe(self)
        self['image'] = self['on-image']
        self['image'].subscribe(self, self.reconfigure)

    def disable(self):
        self.active = False
        self.interface.port.disable()
        self['image'].unsubscribe(self)
        self['image'] = self['off-image']
        self['image'].subscribe(self, self.reconfigure)
    # endregion

