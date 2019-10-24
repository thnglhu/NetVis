from Visual.Canvas import CanvasObject
from abc import ABC, abstractmethod


class Link(CanvasObject, ABC):
    # region Declaration
    def __init__(self, port_1, port_2, bandwidth, canvas):
        super().__init__(canvas)
        self.bandwidth = bandwidth
        self.ports = (port_1, port_2)
        self.subscribers = set()
        self.type = 'link'
        port_1.connect(self)
        port_2.connect(self)
        if not self.ports[0].active or not self.ports[1].active:
            self.active = False
            self.disable()

    def display(self):
        self.canvas.mapped_create_line(
            self,
            *self.ports[0].device.position,
            *self.ports[1].device.position,
            width=3, tag=('link', ), activewidth=5,
            dash=() if self.active else (5, 5))

    def reconfigure(self):
        self.canvas.mapped_itemconfigure(self, width=3, activewidth=5, tag=('link', ), dash=() if self.active else (5, 5))

    def reallocate(self):
        self.canvas.mapped_coords(self, *self.ports[0].device.position, *self.ports[1].device.position)
        for subscriber in self.subscribers:
            subscriber.reallocate()

    def subscribe(self, frame):
        self.subscribers.add(frame)

    def unsubscribe(self, frame):
        self.subscribers.remove(frame)

    def save(self):
        return {
            'ids': [
                self.ports[0].id,
                self.ports[1].id,
            ],
            'bandwidth': self.bandwidth,
        }

    def destroy(self, collector):
        super().destroy(collector)
        self.canvas.mapped_delete(self)
        for subscriber in self.subscribers.copy():
            subscriber.destroy()
        self.ports[0].disconnect()
        self.ports[1].disconnect()
        self.ports[0].link = None
        self.ports[1].link = None
        collector['link'].add(self)

    def modify(self, info):
        self.bandwidth = float(info['bandwidth'])
        for subscriber in self.subscribers:
            subscriber.speed = self.bandwidth
    # endregion

    # region Logical
    def send(self, frame, port):
        from ..Frame import Frame
        from functools import partial
        if port == self.ports[0]:
            Frame(self, True, frame, partial(self.ports[1].receive, frame), self.canvas, self.bandwidth)
        elif port == self.ports[1]:
            Frame(self, False, frame, partial(self.ports[0].receive, frame), self.canvas, self.bandwidth)

    def enable(self):
        if self.ports[0].active and self.ports[1].active:
            self.active = True
            self.reconfigure()

    def disable(self):
        self.active = False
        for subscriber in self.subscribers.copy():
            subscriber.destroy()
        self.reconfigure()
    # endregion
