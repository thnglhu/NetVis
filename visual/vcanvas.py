import tkinter as tk
import numpy as np
from mathplus.geometry import *


class Canvas(tk.Canvas):
    def __init__(self, master=None, cnf=None, **kwargs):
        tk.Canvas.__init__(self, master, cnf, **kwargs)
        if cnf is None:
            cnf = dict()
        self._init_subclass(cnf, **kwargs)

    def _init_subclass(self, cnf, **kwargs):
        self.__scale = 1.0
        self.__angle = 0.0
        self.__size = np.array([kwargs['width'], kwargs['height']])
        self.__graph_objects = dict()
        self.__invert_objects = dict()
        self.__scan_obj = None
        self.__focus_object = None
        self.__target = None
        self.bind("<MouseWheel>", self.__scroll)
        self.bind("<Motion>", self.__scan)
        self.bind("<Double-Button-1>", self.__focus)
        self.bind("<Button-1>", self.__motion_init)
        self.bind("<B1-Motion>", self.__motion)

    def clear(self, *args):
        if args:
            pass
        else:
            tk.Canvas.delete(self, "all")

    def create_mapped_circle(self, base, *args, **kw):
        x, y, radius = args
        position = self.__convert_position(x, y)
        canvas_object = self.__graph_objects.get(base)
        if canvas_object is None:
            self.__graph_objects[base] = tk.Canvas.create_oval(self, *(position - radius), *(position + radius), **kw)
            self.__invert_objects[self.__graph_objects[base], ] = base
        else:
            self.coords(canvas_object, *(position - radius), *(position + radius))
            self.itemconfig(canvas_object, **kw)
        return self.__graph_objects.get(base)

    def create_mapped_line(self, base, *args, **kw):
        a, b, x, y = args
        end_a = self.__convert_position(a, b)
        end_b = self.__convert_position(x, y)
        canvas_object = self.__graph_objects.get(base)
        if canvas_object is None:
            self.__graph_objects[base] = tk.Canvas.create_line(self, *end_a, *end_b, **kw)
            self.__invert_objects[self.__graph_objects[base], ] = base
        else:
            self.coords(canvas_object, *end_a, *end_b)
            self.itemconfig(canvas_object, **kw)
        return self.__graph_objects[base]

    def remove(self, base):
        canvas_object = self.__graph_objects.get(base)
        if canvas_object is not None:
            self.__graph_objects.pop(base)
            self.delete(canvas_object)

    def __convert_position(self, *position):
        return np.array(position) * self.__scale + self.__size / 2

    def __invert_position(self, *position):
        return (position - self.__size / 2) / self.__scale

    def scale_to_fit(self, top_left, bottom_right):
        top_left = np.array(top_left)
        bottom_right = np.array(bottom_right)
        size = bottom_right - top_left
        if (size == 0).any():
            self.__scale = 1
        else:
            scale = self.__size / size
            self.__scale = max(min(scale), 1)
        self.center_to((bottom_right + top_left) / 2)

    def center_to(self, raw_pos):
        center = self.__convert_position(*raw_pos)
        pivot = self.__pivot()
        vector = self.__size / 2
        self.scan_mark(0, 0)
        self.scan_dragto(*(pivot - center + vector).astype(int), gain=1)

    def zoom(self, pos, **kwargs):
        pivot = self.__pivot()
        pos = np.array((self.canvasx(pos[0]), self.canvasy(pos[1])))
        vector = pivot - pos
        pos2 = self.__invert_position(*pos)

        self.__scale += kwargs.get('linear', 0)
        self.__scale *= kwargs.get('potential', 1)

        if self.__scale < 1:
            self.__scale = 1
        pos2 = self.__convert_position(*pos2)
        pivot2 = pos2 + vector
        self.scan_mark(0, 0)
        self.scan_dragto(*(pivot - pivot2).astype(int), gain=1)
        for canvas_object in self.__graph_objects:
            canvas_object.display(self)
        self.fix_order()

    def fix_order(self):
        self.tag_raise('edge')
        self.tag_raise('vertex')
        self.tag_raise('highlight')

    def __pivot(self):
        return self.canvasx(0), self.canvasy(0)

    def __scroll(self, event):
        self.zoom((event.x, event.y), potential=1.2 if event.delta > 0 else 1 / 1.2)

    def __scan(self, event):
        temp = self.find_withtag(tk.CURRENT)
        # if temp != self.__scan_obj:
        #    obj = self.__invert_objects.get(temp, None)
        self.__scan_obj = temp

    def __focus(self, event):
        need_fix = False
        if self.__focus_object:
            self.__focus_object.blur(self)
            need_fix = True
        self.__focus_object = None
        if self.__scan_obj:
            self.__focus_object = self.__invert_objects.get(self.__scan_obj, None)
            if self.__focus_object:
                self.__focus_object.focus(self)
                need_fix = True
        if need_fix:
            self.fix_order()

    def __motion_init(self, event):
        self.last = np.array((event.x, event.y))
        if self.__scan_obj:
            self.__target = self.__invert_objects.get(self.__scan_obj, None)
            from visual import vgraph as vg
            if not isinstance(self.__target, vg.Vertex):
                self.__target = None
            else:
                print(self.coords(self.__scan_obj))
                print(self.__target.attributes['x'], self.__target.attributes['y'])
                print()
        else:
            self.__target = None

    def __motion(self, event):
        new = event.x, event.y
        if self.__target:
            vector = self.__invert_position(*new) - self.__invert_position(*self.last)
            self.__target.motion(self, *vector)
            self.last = np.array(new)
        else:
            new = event.x, event.y
            self.scan_mark(*self.last)
            self.scan_dragto(*new, gain=1)
            self.last = new
