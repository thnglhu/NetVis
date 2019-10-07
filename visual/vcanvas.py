import tkinter as tk
import numpy as np
from mathplus.geometry import *


class Canvas(tk.Canvas):
    subscription = {
        'button-1': {
            'location': set(),
            'location-motion': set(),
            'empty': set(),
            'object': set()
        },
        'button-2': dict(),
        'button-3': {
            'object': set(),
            'empty': set()
        },
        'motion': set(),
    }
    cache = dict()
    last = (0, 0)

    def __init__(self, master=None, cnf=None, **kwargs):
        tk.Canvas.__init__(self, master, cnf, **kwargs)
        if cnf is None:
            cnf = dict()
        self.__init_subclass(cnf, **kwargs)

    def __init_subclass(self, cnf=None, **kwargs):
        self.__size = np.array([kwargs['width'], kwargs['height']])
        self.__scale = 1.0
        self.__graph_objects = dict()
        self.__invert_objects = dict()
        self.__scan_obj = None
        self.__focus_object = None
        self.__target = None
        self.__movable = True
        self.__sender_turn = True
        self.subscriber = dict()
        self.bind("<MouseWheel>", self.__scroll)
        self.bind("<Motion>", self.__scan)
        self.bind("<Button-1>", self.__motion_init)
        self.bind("<B1-Motion>", self.__motion)
        self.bind("<Configure>", self.__resize)

    def clear(self, *args):
        self.delete("all")
        self.__graph_objects = dict()

    def create_mapped_circle(self, base, *args, **kw):
        canvas_object = self.__graph_objects.get(base)
        if canvas_object is None:
            x, y, radius = args
            position = self.convert_position(x, y)
            self.__graph_objects[base] = tk.Canvas.create_oval(self, *(position - radius), *(position + radius), **kw)
            self.__invert_objects[self.__graph_objects[base], ] = base
        return self.__graph_objects.get(base)

    def create_mapped_line(self, base, *args, **kw):
        canvas_object = self.__graph_objects.get(base)
        if canvas_object is None:
            a, b, x, y = args
            end_a = self.convert_position(a, b)
            end_b = self.convert_position(x, y)
            self.__graph_objects[base] = tk.Canvas.create_line(self, *end_a, *end_b, **kw)
            self.__invert_objects[self.__graph_objects[base], ] = base
            from visual import vgraph as vg
            canvas_object = self.__graph_objects.get(base)
            if isinstance(base, vg.Edge):
                self.tag_bind(canvas_object, '<Button-1>', self.__edge_button, ('button-1', base))

        return self.__graph_objects[base]

    def create_mapped_image(self, base, *args, **kw):
        canvas_object = self.__graph_objects.get(base)
        if canvas_object is None:
            position = self.convert_position(*args)
            self.__graph_objects[base] = tk.Canvas.create_image(self, *position, **kw)
            self.__invert_objects[self.__graph_objects[base], ] = base

            from visual import vnetwork as vn
            canvas_object = self.__graph_objects.get(base)
            if isinstance(base, vn.VVertex):
                self.tag_bind(canvas_object, '<Button-1>', self.__vertex_button, ('button-1', base))
                self.tag_bind(canvas_object, '<B1-Motion>', self.__vertex_button_motion, ('button-1', base))
                self.tag_bind(canvas_object, '<ButtonRelease-1>', self.__vertex__button_release, ('button-1', ))
                self.tag_bind(canvas_object, '<Button-3>', self.__vertex_button, ('button-3', base))
                self.tag_bind(canvas_object, '<B3-Motion>', self.__vertex_button_motion, ('button-3', base))
                self.tag_bind(canvas_object, '<ButtonRelease-3>', self.__vertex__button_release, ('button-3',))

    def tag_bind(self, tagOrId, sequence=None, func=None, args=None):
        def _func(event):
            if args: func(event, *args)
            else: func(event)
        super().tag_bind(tagOrId, sequence, _func)

    def coords_mapped(self, base, *args):
        from visual import vgraph as vg
        canvas_object = self.__graph_objects.get(base)
        if canvas_object:
            position = self.convert_position(*args[:2]).astype(float)
            from visual import vnetwork as vn
            if isinstance(base, vn.Frame):
                pass
            elif isinstance(base, vn.VVertex):
                pass
            elif isinstance(base, vg.Edge):
                position = np.concatenate((position, self.convert_position(*(args[2:4]))))
            else:
                raise ValueError
            self.coords(canvas_object, *position)
        else:
            print(canvas_object)
            raise TypeError

    def itemconfig_mapped(self, base, **kwargs):
        canvas_object = self.__graph_objects.get(base)
        if canvas_object is not None:
            self.itemconfigure(canvas_object, **kwargs)
        else:
            raise TypeError

    def remove(self, base):
        canvas_object = self.__graph_objects.get(base)
        if canvas_object is not None:
            self.__graph_objects.pop(base)
            self.delete(canvas_object)

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
            canvas_object.reallocate(self)
        self.fix_order()

    def reconfigure(self):
        for canvas_object in self.__graph_objects:
            canvas_object.reconfigure(self)
        self.fix_order()

    def fix_order(self):
        self.tag_raise('edge')
        self.tag_raise('vertex')
        self.tag_raise('frame')

    def __pivot(self):
        return self.canvasx(0), self.canvasy(0)

    def __scroll(self, event):
        self.zoom((event.x, event.y), potential=1.2 if event.delta > 0 else 1 / 1.2)

    def __scan(self, event):
        self.__update_mouse_location(event.x, event.y)

    def __motion_init(self, event):
        self.__update_mouse_location(event.x, event.y)
        self.__button_location('button-1', event)

    def __motion(self, event):
        new = event.x, event.y
        if self.__movable:
            self.scan_mark(*self.last)
            self.scan_dragto(*new, gain=1)
        self.__update_mouse_location(*new)

    def __vertex_button(self, event, button, device):
        self.__button_object(button, device)
        self.__update_mouse_location(event.x, event.y)
        self.__button_empty(button, device)
        if button == 'button-1':
            self.__movable = False

    def __vertex_button_motion(self, event, button, device):
        new = event.x, event.y
        if button == 'button-1':
            vector = self.invert_position(*new) - self.invert_position(*self.last)
            device.motion(self, *vector)
        self.__update_mouse_location(event.x, event.y)

    def __vertex__button_release(self, event, button):
        if button == 'button-1':
            self.__movable = True

    def __edge_button(self, event, button, link):
        self.__button_object(button, link)

    def __resize(self, event):
        self.__size[0] = event.width
        self.__size[1] = event.height
        self.reallocate()

    def __update_mouse_location(self, x, y):
        self.last = x, y
        for subscriber in self.subscription['motion'].copy():
            subscriber.trigger(x + self.canvasx(0), y + self.canvasy(0))

    def __button_location(self, button, event):
        for subscriber in self.subscription[button]['location'].copy():
            x, y = np.array((self.canvasx(0), self.canvasy(0))) + (event.x, event.y)
            subscriber.trigger(x, y)

    def __button_object(self, button, target):
        if target:
            for subscriber in self.subscription[button]['object'].copy():
                subscriber.set_variable(target)
                subscriber.trigger(target.info())

    def __button_empty(self, button, target):
        if target:
            for subscriber in self.subscription[button]['empty'].copy():
                subscriber.set_variable(target)
                subscriber.trigger()

    def subscribe(self, func, *args):
        if func in self.cache:
            return
        location = self.subscription
        for sub in args:
            location = location[sub]
        self.cache[func] = Warp(func)
        location.add(self.cache[func])

    def unsubscribe(self, func, *args):
        if func not in self.cache:
            return
        location = self.subscription
        for sub in args:
            location = location[sub]
        function = self.cache[func]
        if function not in location:
            return
        location.remove(function)
        del self.cache[func]

    @staticmethod
    def convert(canvas):
        if isinstance(canvas, Canvas):
            raise NotImplementedError
        canvas.__class__ = Canvas
        height = canvas.winfo_height()
        width = canvas.winfo_width()
        canvas.__init_subclass(width=width, height=height)
        return canvas


class Warp:
    def __init__(self, function, variable=None):
        self.function = function
        self.variable = variable

    def trigger(self, *args):
        self.function(*args)

    def set_variable(self, value):
        self.variable = value

    def get_variable(self):
        return self.variable
