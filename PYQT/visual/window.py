import tkinter as tk
class Window(tk.Frame):
    def __init__(self, master=None, *cnf, **kw):
        tk.Frame.__init__(self, master, cnf, **kw)
        self.master = master
        self.__init_window()
    def __init_window(self):
        self.master.title("Network visualization")
        self.pack(fill=tk.BOTH, expand=1)
        test = tk.Button(self, text="test")
        test.place(x=50, y=50)
