
# TODO edit GUI here
"""
    DO NOT GENERATE GUI_SUPPORT again
    top_level: gui
"""
import sys
import tkinter as tk
from tkinter import filedialog
# from controller import application
from gui import *
import tkinter.ttk as ttk

# controller = application.Controller.get_instance()


def exit_window():
    # TODO popup save data, clean threads, ... (if exist)
    # controller.exit()
    destroy_window()
    sys.stdout.flush()


def open_file():
    file = filedialog.askopenfile(
        title="Select file",
        filetypes=(("GraphML", "*.graphml"), ("Text file", "*.txt")))
    # controller.load(file, w.canvas)
    sys.stdout.flush()


def create_new_file():
    print("Create")


def open_recent_file():
    print("Recent")


def save_file():
    print("Save")


def save_file_as():
    file = filedialog.asksaveasfilename(
        initialdir="/", title="Select file",
        filetypes=(("jpeg files", "*.jpg"), ("Text files", "*.txt")))
    print(file, file.__class__)


def close():
    print("Close")


def undo():
    print("Undo")


def redo():
    print("Redo")


def zoom_in():
    print("Zoom in")


def zoom_out():
    print("Zoom out")


def print_file():
    print("Print")


def find_node():
    print("Find node")


def find_edge():
    print("Find edge")


def cut():
    print("Cut")


def copy():
    print("Copy")


def paste():
    print("Paste")


def select_all():
    print("Select All")


def select_all_nodes():
    print("Select All Nodes")


def deselect_all_nodes():
    print("Deselect All Nodes")


def add_node():
    print("Add Node")


def remove_node():
    print("Remove Node")


def rename_node():
    print("Rename Node")


def select_node_properties():
    print("Properties of Node")


def change_all_nodes_color():
    print("Change all node color")


def change_all_nodes_size():
    print("Change all node size")


def change_all_nodes_shape():
    print("Change all node shape")


def change_all_nodes_label_size():
    print("Change all node's label size")


def change_all_nodes_label_color():
    print("Change all node's label color")


def select_all_edges():
    print("Select All Edges")


def deselect_all_edges():
    print("Deselect All Edges")


def add_edge():
    print("Add Edge")


def remove_edge():
    print("Remove Edge")


def select_edge_properties():
    print("Select Edge Properties")


def change_all_edges_label():
    print("Change All Edges Label")


def change_all_edges_color():
    print("Change All Edges color")


def change_all_edges_weight():
    print("Change All Edges Weight")


def settings():
    print('gui_support.settings')
    sys.stdout.flush()


def init(top, gui, *args, **kwargs):
    global w, top_level, root
    w = gui
    top_level = top
    root = top
    print(w.__class__)


def destroy_window():
    # Function which closes the window.
    global top_level
    top_level.destroy()
    top_level = None





