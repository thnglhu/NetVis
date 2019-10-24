from .vertex import Vertex
from ..port import Port

from Resource import get_image


class Hub(Vertex):

    # region Canvas declaration
    def __init__(self, canvas, info):
        super().__init__(canvas)
        self.position = info['position']
        self.name = info['name']
        self.ports = {
            Port(port['name'], self, port.get('id')) for port in info['ports']
        }
        self.type = 'hub'
        self.active = info['status']
        if not self.active:
            for port in self.ports:
                port.disable()
        self['image'] = self['on-image'] if self.active else self['off-image']

    def _set_image(self):
        self['on-image'] = get_image('_hub-on')
        self['off-image'] = get_image('_hub-off')

    def get_ports(self):
        return self.ports

    def save(self):
        return {
            'type': self.type,
            'status': self.active,
            'name': self.name,
            'position': tuple(self.position),
            'ports': [
                port.save() for port in self.ports
            ]
        }

    def destroy(self, collector):
        super().destroy(collector)
        for port in self.ports:
            port.destroy(collector)
    # endregion

    # region Logical
    def receive(self, frame, port):
        for other in self.ports:
            if other != port:
                other.send(frame)
        return True

    def enable(self):
        self.active = True
        for port in self.ports:
            port.enable()
        self['image'].unsubscribe(self)
        self['image'] = self['on-image']
        self['image'].subscribe(self, self.reconfigure)

    def disable(self):
        self.active = False
        for port in self.ports:
            port.disable()
        self['image'].unsubscribe(self)
        self['image'] = self['off-image']
        self['image'].subscribe(self, self.reconfigure)

    def disconnect(self, port):
        pass

    def modify(self, info):
        self['name'] = info['name']
    # endregion
