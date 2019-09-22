import tkinter as tk
import numpy as np
from mathplus.geometry import *
class Canvas(tk.Canvas):
    def __init__(self, master=None, cnf=dict(), **kwargs):
        tk.Canvas.__init__(self, master, cnf, **kwargs)
        self.__scale = 1.0
        self.__angle = 0.0
        self.__size = np.array([kwargs['width'], kwargs['height']])
        self.__objects = dict()
        self.__invert_objects = dict()
        self.__scan_obj = None
        self.__focus_object = None
        self.__target = None
        self.bind("<Button-2>", self.__motion_init)
        self.bind("<B2-Motion>", self.__motion)
        self.bind("<MouseWheel>", self.__scroll)
        self.bind("<Motion>", self.__scan)
        self.bind("<Double-Button-1>", self.__focus)
        self.bind("<Button-1>", self.__motion2_init)
        self.bind("<B1-Motion>", self.__motion2)
    def clear(self, *args):
        if args:
            pass
        else:
            tk.Canvas.delete(self, "all")
    def create_mapped_circle(self, base, *args, **kw):
        x, y, radius = args
        position = self.__convert_position(x, y)
        object = self.__objects.get(base)
        if object is None:
            #if point_is_inside_rect(position, [-radius, -radius], self.__size + [radius, radius]):
            self.__objects[base] = tk.Canvas.create_oval(self, *(position - radius), *(position + radius), **kw)
            self.__invert_objects[self.__objects[base],] = base
        else:
            self.coords(object, *(position - radius), *(position + radius))
            self.itemconfig(object, **kw)
        return self.__objects.get(base)

    def create_mapped_line(self, base, *args, **kw):
        a, b, x, y = args
        position_A = self.__convert_position(a, b)
        position_B = self.__convert_position(x, y)
        object = self.__objects.get(base)
        if object is None:
            #top_left, bottom_right = [0, 0], self.__size
            #if     point_is_inside_rect(position_A, top_left, bottom_right) \
            #    or point_is_inside_rect(position_B, top_left, bottom_right) \
            #    or segments_are_collided_rect(position_A, position_B, top_left, bottom_right):
            self.__objects[base] = tk.Canvas.create_line(self, *position_A, *position_B, **kw)
            self.__invert_objects[self.__objects[base],] = base
        else:
            self.coords(object, *position_A, *position_B)
            self.itemconfig(object, **kw)
        return self.__objects[base]

    def __convert_position(self, *position):
        return np.array(position) * self.__scale + self.__size / 2

    def __invert_position(self, *position):
        return (position - self.__size / 2) / self.__scale

    def scale_to_fit(self, top_left, bottom_right):
        top_left = np.array(top_left)
        bottom_right = np.array(bottom_right)
        size = bottom_right - top_left
        if (size == 0).any(): self.__scale = 1
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

        if self.__scale < 1: self.__scale = 1
        pos2 = self.__convert_position(*pos2)
        pivot2 = pos2 + vector
        self.scan_mark(0, 0)
        self.scan_dragto(*(pivot - pivot2).astype(int), gain=1)
        for object in self.__objects: object.display(self)
        self.fix_order()

    def fix_order(self):
        self.tag_raise('edge')
        self.tag_raise('vertex')
        self.tag_raise('edge-highlight')
        self.tag_raise('vertex-highlight')
    def __pivot(self):
        return self.canvasx(0), self.canvasy(0)

    def __motion_init(self, event):
        self.last = event.x, event.y

    def __motion(self, event):
        new = event.x, event.y
        self.scan_mark(*self.last)
        self.scan_dragto(*new, gain=1)
        self.last = new

    def __scroll(self, event):
        self.zoom((event.x, event.y), potential=1.2 if event.delta > 0 else 1/1.2)

    def __scan(self, event):
        temp = self.find_withtag(tk.CURRENT)
        if temp != self.__scan_obj: obj = self.__invert_objects.get(temp, None)
            # if obj: obj.visual()

        #if temp == self.__scan_obj:
            #print(temp, self.__invert_objects.get(temp, None))
            #print(self.gettags(tk.CURRENT))

            #self.itemconfig(self.__scan_obj, fill="red")
        self.__scan_obj = temp
    def __focus(self, event):
        self.__focus_object and self.__focus_object.unfocus(self)
        self.__focus_object = None
        if self.__scan_obj:
            self.__focus_object = self.__invert_objects.get(self.__scan_obj, None)
            self.__focus_object and self.__focus_object.focus(self)
    def __motion2_init(self, event):
        self.last2 = np.array((event.x, event.y))
        if self.__scan_obj:
            self.__target = self.__invert_objects.get(self.__scan_obj, None)
            from visual import vgraph as vg
            if not isinstance(self.__target, vg.Vertex): self.__target = None
        else:
            self.__target = None

    def __motion2(self, event):
        new = event.x, event.y
        if self.__target:
            # print()
            # vector = self.last2 - new
            # print(vector)
            vector = self.__invert_position(*new) - self.__invert_position(*self.last2)
            self.__target.motion(self, *vector)
            self.last2 = np.array(new)

