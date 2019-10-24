import tkinter as tk


class VerticalScrollable(tk.Frame):
    def __init__(self, frame, width=16):
        scrollbar = tk.Scrollbar(frame, width=width)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
        self.canvas = tk.Canvas(frame, yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=self.canvas.yview)
        self.canvas.bind('<Configure>', self.__fill_canvas)
        tk.Frame.__init__(self, frame)
        self.windows_item = self.canvas.create_window(0, 0, window=self, anchor=tk.NW)

    def __fill_canvas(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.windows_item, width=canvas_width)

    def update(self):
        self.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(self.windows_item))


class HorizontalScrollable(tk.Frame):
    def __init__(self, frame, width=16):
        scrollbar = tk.Scrollbar(frame, width=width, orient=tk.HORIZONTAL)
        scrollbar.pack(side=tk.BOTTOM, fill=tk.X, expand=False)
        self.canvas = tk.Canvas(frame, xscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.canvas.xview)
        self.canvas.bind('<Configure>', self.__fill_canvas)
        tk.Frame.__init__(self, frame)
        self.windows_item = self.canvas.create_window(0, 0, window=self, anchor=tk.NW)

    def __fill_canvas(self, event):
        canvas_height = event.height
        self.canvas.itemconfig(self.windows_item, height = canvas_height)

    def update(self):
        self.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(self.windows_item))