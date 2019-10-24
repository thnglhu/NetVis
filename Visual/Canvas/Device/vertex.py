from Visual.Canvas import CanvasObject
from abc import ABC, abstractmethod


class Vertex(CanvasObject, ABC):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.position = (0, 0)
        self._set_image()
        self.edges = set()
        self.type = 'abstract'

    @abstractmethod
    def _set_image(self):
        pass

    @staticmethod
    def load(info, canvas):
        pass

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def get_ports(self):
        pass

    def display(self):
        self.canvas.mapped_create_image(self, *self.position, image=self['image'].get_image(), tag=('device', ))
        self['image'].subscribe(self, self.reconfigure)

    def reconfigure(self):
        self.canvas.mapped_itemconfigure(self, image=self['image'].get_image())

    def reallocate(self):
        self.canvas.mapped_coords(self, *self.position)

    def destroy(self, collector):
        super().destroy(collector)
        self.canvas.mapped_delete(self)
        self['image'].unsubscribe(self)
        collector['device'].add(self)

    def move(self, delta):
        self.position = tuple(self.position + delta)
        self.reallocate()
        for edge in self.edges:
            edge.reallocate()

    def subscribe(self, edge):
        self.edges.add(edge)

    def unsubscribe(self, edge):
        self.edges.remove(edge)
