import tkinter as tk
import numpy as np
from mathplus.geometry import *


class Canvas(tk.Canvas):
    subscription = {
        'button-1': {
            'location': set(),
            'location-motion': set(),
            'object': set()
        },
        'button-2': dict(),
        'button-3': dict(),
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
        self.bind("<Double-Button-3>", self.__double)
        self.bind("<Button-1>", self.__motion_init)
        self.bind("<B1-Motion>", self.__motion)
        self.bind("<Configure>", self.__resize)

    def clear(self, *args):
        if args:
            pass
        else:
            tk.Canvas.delete(self, "all")

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
        return self.__graph_objects[base]

    def create_mapped_image(self, base, *args, **kw):
        canvas_object = self.__graph_objects.get(base)
        if canvas_object is None:
            position = self.convert_position(*args)
            self.__graph_objects[base] = tk.Canvas.create_image(self, *position, **kw)
            self.__invert_objects[self.__graph_objects[base],] = base

    def coords_mapped(self, base, *args):
        from visual import vgraph as vg
        canvas_object = self.__graph_objects.get(base)
        if canvas_object is not None:
            position = self.convert_position(*args[:2]).astype(float)
            from visual import vnetwork as vn
            if isinstance(base, vn.Frame):
                rad = args[2]
                position = np.concatenate((position - rad, position + rad))
            elif isinstance(base, vn.VVertex):
                pass
            elif isinstance(base, vg.Edge):
                position = np.concatenate((position, self.convert_position(*(args[2:4]))))
            else:
                raise ValueError
            self.coords(canvas_object, *position)
        else:
            raise TypeError

    def itemconfig_mapped(self, base, **kwargs):
        canvas_object = self.__graph_objects.get(base)
        if canvas_object is not None:
            self.itemconfig(canvas_object, **kwargs)
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

    def scale_to_fit(self, top_left, bottom_right):
        top_left = np.array(top_left)
        bottom_right = np.array(bottom_right)
        top_left[0], bottom_right[0] = sorted((top_left[0], bottom_right[0]))
        top_left[1], bottom_right[1] = sorted((top_left[1], bottom_right[1]))
        size = bottom_right - top_left
        print(size)
        if (size == 0).any():
            self.__scale = 1
        else:
            scale = self.__size / size
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
        self.__scan_obj = self.find_withtag(tk.CURRENT)
        self.__update_mouse_location(event.x, event.y)

    def __double(self, event):
        if self.__sender_turn:
            self.sender = self.__invert_objects.get(self.__scan_obj, None)
            from visual import vnetwork as vn
            if not isinstance(self.sender, vn.PC):
                pass
            else:
                self.__sender_turn = False
                self.sender.focus(self)
        else:
            self.receiver = self.__invert_objects.get(self.__scan_obj, None)
            from visual import vnetwork as vn
            if not isinstance(self.receiver, vn.PC):
                pass
            else:
                print(self.sender, self.receiver)
                self.sender.send(self, self.receiver.interface.ip_address)
                self.sender.unfocus(self)
                self.sender = self.receiver = None
                self.__sender_turn = True

    def __motion_init(self, event):
        self.__update_mouse_location(event.x, event.y)
        self.__button_1_location(event)
        self.__button_1_object(event)
        if self.__scan_obj:
            self.__target = self.__invert_objects.get(self.__scan_obj)
            from visual import vgraph as vg
            if not isinstance(self.__target, vg.Vertex):
                self.__target = None
        else:
            self.__target = None

    def __motion(self, event):
        new = event.x, event.y
        if self.__movable and self.__target:
            vector = self.invert_position(*new) - self.invert_position(*self.last)
            self.__target.motion(self, *vector)
        else:
            new = event.x, event.y
            self.scan_mark(*self.last)
            self.scan_dragto(*new, gain=1)
        self.__update_mouse_location(*new)

    def __resize(self, event):
        self.__size[0] = event.width
        self.__size[1] = event.height
        self.reallocate()

    def __update_mouse_location(self, x, y):
        self.last = x, y
        for subscriber in self.subscription['motion']:
            subscriber.trigger(x + self.canvasx(0), y + self.canvasy(0))

    def __button_1_location(self, event):
        # qualified = False
        for subscriber in self.subscription['button-1']['location']:
            x, y = np.array((self.canvasx(0), self.canvasy(0))) + self.last
            subscriber.trigger(x, y)
            # qualified = True
        # if qualified:
        #    self.__scan(event)

    def __button_1_object(self, event):
        target = self.__invert_objects.get(self.__scan_obj)
        if target:
            for subscriber in self.subscription['button-1']['object']:
                subscriber.trigger(target.info())
                subscriber.set_variable(target)

    def subscribe(self, func, *args):
        print(func)
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
        self.cache.remove(func)
        if func in self.variable:
            del self.variable[func]

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
