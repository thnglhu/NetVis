import tkinter as tk
import numpy as np
from abc import ABC, abstractmethod
from functools import partial


class Canvas(tk.Canvas):
    subscription = {
        'Button-1': {
            'location': set(),
            'location-motion': set(),
            'empty': set(),
            'object': set(),
            'nullable-object': set()
        },
        'Button-2': dict(),
        'Button-3': {
            'object': set(),
            'empty': set()
        },
        'Motion': set(),
    }
    cache = set()
    last = (0, 0)

    def __init__(self, master=None, **kwargs):
        tk.Canvas.__init__(self, master, **kwargs)
        self.__size = np.array([self['width'], self['height']]).astype(float)
        self.__scale = 1.0
        self.__graph_objects = dict()
        self.__invert_objects = dict()
        self.subscriber = dict()
        self.movable = True
        self.bind("<MouseWheel>", self.__scroll)
        self.bind("<Motion>", self.__scan)
        self.bind("<Button-1>", self.__motion_init)
        self.bind("<B1-Motion>", self.__motion)
        self.bind("<Configure>", self.__resize)

    def clear(self, *args):
        pass

    def mapped_create_line(self, base, *args, **kw):
        canvas_object = self.__graph_objects.get(base)
        if canvas_object is None:
            a, b, x, y = args
            end_a = self.convert_position(a, b)
            end_b = self.convert_position(x, y)
            canvas_object = tk.Canvas.create_line(self, *end_a, *end_b, **kw)
            self.__graph_objects[base] = {
                "type": "line",
                "object": canvas_object,
            }
            self.__invert_objects[self.__graph_objects[base]["object"], ] = base
            self.tag_bind(canvas_object, "<Button-1>", self.__device_button, ('Button-1', base))
            self.fix_tag()

    def mapped_create_image(self, base, *args, **kw):
        canvas_object = self.__graph_objects.get(base)
        if canvas_object is None:
            position = self.convert_position(*args)
            canvas_object = tk.Canvas.create_image(self, *position, **kw)
            self.__graph_objects[base] = {
                "type": "image",
                "object": canvas_object,
            }
            self.__invert_objects[self.__graph_objects[base]["object"], ] = base
            self.tag_bind(canvas_object, "<Button-1>", self.__device_button, ('Button-1', base))
            self.tag_bind(canvas_object, "<Button-3>", self.__device_button, ('Button-3', base))
            self.tag_bind(canvas_object, "<B1-Motion>", self.__device_button_motion, ('Button-1', base))
            self.tag_bind(canvas_object, "<ButtonRelease-1>", self.__device_button_release, ('Button-1', ))
            self.fix_tag()

    def tag_bind(self, tagOrId, sequence=None, func=None, add=None):
        super().tag_bind(tagOrId, sequence, partial(func, *add))

    def mapped_coords(self, base, *args):
        canvas_object = self.__graph_objects.get(base)
        if canvas_object:
            backup = list()
            for pair in zip(args[::2], args[1::2]):
                backup.extend(self.convert_position(*pair))
            self.coords(canvas_object["object"], *backup)

    def mapped_itemconfigure(self, base, **kwargs):
        canvas_object = self.__graph_objects.get(base)
        if canvas_object:
            self.itemconfigure(canvas_object["object"], **kwargs)

    def mapped_delete(self, base):
        canvas_object = self.__graph_objects.get(base)
        if canvas_object:
            self.delete(canvas_object['object'])
            self.__invert_objects.pop((canvas_object['object'],))
            self.__graph_objects.pop(base)

    def convert_position(self, *position):
        return np.array(position) * self.__scale + self.__size / 2

    def invert_position(self, *position):
        return (position - self.__size / 2) / self.__scale

    def scale_to_fit(self, top_left, bottom_right, offset):
        top_left = np.array(top_left)
        bottom_right = np.array(bottom_right)
        top_left[0], bottom_right[0] = sorted((top_left[0], bottom_right[0]))
        top_left[1], bottom_right[1] = sorted((top_left[1], bottom_right[1]))
        size = bottom_right - top_left
        if (size == 0).any():
            self.__scale = 1
        else:
            scale = (self.__size - offset) / size
            self.__scale = max(min(scale), 1)
        self.center_to((bottom_right + top_left) / 2)
        self.reallocate()

    def center_to(self, raw_pos):
        center = self.convert_position(*raw_pos)
        pivot = self.__pivot()
        vector = self.__size / 2
        self.scan_mark(0, 0)
        self.scan_dragto(*(pivot - center + vector).astype(int), gain=1)

    def zoom(self, pos, **kwargs):
        pivot = self.__pivot()
        pos = np.array((self.canvasx(pos[0]), self.canvasy(pos[1])))
        vector = pivot - pos
        pos2 = self.invert_position(*pos)

        self.__scale += kwargs.get('linear', 0)
        self.__scale *= kwargs.get('potential', 1)

        if self.__scale < 1:
            self.__scale = 1
        pos2 = self.convert_position(*pos2)
        pivot2 = pos2 + vector
        self.scan_mark(0, 0)
        self.scan_dragto(*(pivot - pivot2).astype(int), gain=1)
        self.reallocate()

    def reallocate(self):
        for canvas_object in self.__graph_objects:
            canvas_object.reallocate()

    def reconfigure(self):
        for canvas_object in self.__graph_objects:
            canvas_object.reconfigure()

    def fix_tag(self):
        self.tag_raise('frame')
        self.tag_lower('link')

    def __pivot(self):
        return self.canvasx(0), self.canvasy(0)

    def __scroll(self, event):
        self.zoom((event.x, event.y), potential=1.2 if event.delta > 0 else 1 / 1.2)

    def __scan(self, event):
        self.__update_mouse_location(event.x, event.y)

    def __motion_init(self, event):
        self.__update_mouse_location(event.x, event.y)
        self.__button_location('Button-1', event)

    def __motion(self, event):
        new = event.x, event.y
        if self.movable:
            self.scan_mark(*self.last)
            self.scan_dragto(*new, gain=1)
        self.__update_mouse_location(*new)

    def __device_button(self, button, device, event):
        self.__button_object(button, device)
        self.__update_mouse_location(event.x, event.y)
        self.__button_empty(button, device)
        if button == 'Button-1':
            self.movable = False

    def __device_button_motion(self, button, device, event):
        new = event.x, event.y
        if button == 'Button-1':
            vector = self.invert_position(*new) - self.invert_position(*self.last)
            if event.x < self.__size[0] / 10 and vector[0] < 0:
                self.scan_mark(event.x, event.y)
                self.scan_dragto(event.x + 5, event.y, gain=1)
                vector[0] -= 5 / self.__scale
            elif event.x > self.__size[0] * 9 / 10 and vector[0] > 0:
                self.scan_mark(event.x, event.y)
                self.scan_dragto(event.x - 5, event.y, gain=1)
                vector[0] += 5 / self.__scale
            if event.y < self.__size[1] / 10 and vector[1] < 0:
                self.scan_mark(event.x, event.y)
                self.scan_dragto(event.x, event.y + 5, gain=1)
                vector[1] -= 5 / self.__scale
            elif event.y > self.__size[1] * 9 / 10 and vector[1] > 0:
                self.scan_mark(event.x, event.y)
                self.scan_dragto(event.x, event.y - 5, gain=1)
                vector[1] += 5 / self.__scale
            device.move(vector)
        self.__update_mouse_location(event.x, event.y)

    def __device_button_release(self, button, _):
        if button == 'Button-1':
            self.movable = True

    def __edge_button(self, _, button, link):
        self.__button_object(button, link)
        self.__button_empty(button, link)

    def __resize(self, event):
        self.__size[0] = event.width
        self.__size[1] = event.height
        self.reallocate()

    def __update_mouse_location(self, x, y):
        self.last = x, y
        for subscriber in self.subscription['Motion'].copy():
            subscriber(x + self.canvasx(0), y + self.canvasy(0))

    def __button_location(self, button, event):
        for subscriber in self.subscription[button]['location'].copy():
            x, y = np.array((self.canvasx(0), self.canvasy(0))) + (event.x, event.y)
            subscriber(x, y)

    def __button_object(self, button, target):
        if target:
            for subscriber in self.subscription[button]['object'].copy():
                subscriber(target)

    def __button_empty(self, button, target):
        if target:
            for subscriber in self.subscription[button]['empty'].copy():
                subscriber()

    def __escape(self, event):
        for subscriber in self.subscription['Escape'].copy():
            subscriber()

    def subscribe(self, func, *args):
        if func in self.cache:
            return
        location = self.subscription
        for sub in args:
            location = location[sub]
        self.cache.add(func)
        location.add(func)

    def unsubscribe(self, func, *args):
        if func not in self.cache:
            return
        location = self.subscription
        for sub in args:
            location = location[sub]
        location.remove(func)
        self.cache.remove(func)


class CanvasObject(ABC):

    def __init__(self, canvas):
        self.attributes = dict()
        self.canvas = canvas
        self.active = True
        self.destroyed = False
        self.inspector = None

    def __getitem__(self, item):
        return self.attributes.get(item)

    def __setitem__(self, key, value):
        self.attributes[key] = value

    @abstractmethod
    def display(self):
        pass

    @abstractmethod
    def reallocate(self):
        pass

    @abstractmethod
    def reconfigure(self):
        pass

    @abstractmethod
    def enable(self):
        pass

    @abstractmethod
    def disable(self):
        pass

    def update(self):
        if self.inspector:
            self.inspector(self)

    def set_inspector(self, inspector):
        self.inspector = inspector

    def remove_inspector(self):
        self.inspector = None

    def destroy(self, collector):
        self.destroyed = True
        if self.inspector:
            self.inspector(None)

