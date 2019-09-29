
# TODO edit GUI here
"""
    DO NOT GENERATE GUI_SUPPORT again
    top_level: gui
"""
import sys
import tkinter as tk
from tkinter import filedialog
from controller import application
import tkinter.ttk as ttk

controller = application.Controller.get_instance()


def exit():
    # TODO popup save data, clean threads, ... (if exist)
    controller.exit()
    destroy_window()
    sys.stdout.flush()


def load_file():
    file = filedialog.askopenfile(
        title="Select file",
        filetypes=(("GraphML", "*.graphml"), ("Text file", "*.txt"))
    )
    controller.load(file, w.canvas)
    sys.stdout.flush()


def settings():
    print('gui_support.settings')
    sys.stdout.flush()


def init(top, gui, *args, **kwargs):
    global w, top_level, root
    w = gui
    top_level = top
    root = top
    import test
    test.super_test(w.canvas)


def destroy_window():
    # Function which closes the window.
    global top_level
    top_level.destroy()
    top_level = None

def test():
    # controller.filter(target="vertex", criteria=("GeoLocation", ""))
    w.canvas.tag_raise('vertex')
    controller.test()
    pass




