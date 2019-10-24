from Visual.Canvas import CanvasObject
from numpy import array
from threading import Thread
from random import uniform
import setting


class Frame(CanvasObject):
    def disable(self):
        pass

    def enable(self):
        pass

    def __init__(self, link, direct, frame, delegate, canvas, speed):
        super().__init__(canvas)
        if not setting.visible.get(frame.get_name(), True):
            delegate()
            return
        self.is_dropping = False
        self.dropping_vector = array((uniform(-2, 2), uniform(-2, 2)))
        self.link = link
        self.direct = direct
        self.frame = frame
        self.delegate = delegate
        self.ports = link.ports[::1 if direct else -1]
        self['image'] = frame.get_image()
        self.progress = 0
        self.speed = speed
        link.subscribe(self)
        Thread(target=self.sending).start()
        self.display()
        self.type = 'frame'

    def sending(self):
        from time import sleep
        out = False
        while self.progress < 1.0:
            sleep(1/30)
            if not setting.visible.get(self.frame.get_name(), True):
                out = True
                break
            if self.destroyed:
                return
            self.reallocate()
            self.progress += 0.01 * self.speed * setting.time_scale.get() / 100
        if out:
            self.delegate()
            self.canvas.mapped_delete(self)
            self.link.unsubscribe(self)
            return
        self.progress = 1.0
        self.reallocate()
        if not self.delegate():
            self.is_dropping = True
            self.progress = 0
            Thread(target=self.dropping).start()
        else:
            self.canvas.mapped_delete(self)
            self.link.unsubscribe(self)

    def dropping(self):
        from time import sleep
        while self.progress < 1.0:
            sleep(1/30)
            if not setting.visible.get(self.frame.get_name(), True):
                self.canvas.mapped_delete(self)
                self.link.unsubscribe(self)
                return
            if self.destroyed:
                return
            self.reallocate()
            self.progress += 0.5 * setting.time_scale.get() / 100
        self.progress = 1.0
        self.reallocate()
        self.canvas.mapped_delete(self)
        self.link.unsubscribe(self)

    def __location(self):
        if not self.is_dropping:
            return array(self.ports[0].device.position) + (array(self.ports[1].device.position) - array(self.ports[0].device.position)) * self.progress
        else:
            return array(self.ports[1].device.position) + self.dropping_vector * self.progress

    def display(self):
        self.canvas.mapped_create_image(self, *self.__location(), image=self['image'].get_image(), tag=('frame', ))
        self['image'].subscribe(self, self.reconfigure)

    def reallocate(self):
        self.canvas.mapped_coords(self, *self.__location())

    def reconfigure(self):
        self.canvas.mapped_itemconfigure(self, image=self['image'].get_image())

    def destroy(self, _=None):
        super().destroy(_)
        self.canvas.mapped_delete(self)
        self['image'].unsubscribe(self)
        self.link.unsubscribe(self)
