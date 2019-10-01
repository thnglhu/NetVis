# TODO edit GUI here
"""
    DO NOT GENERATE GUI_SUPPORT again
    top_level: gui
"""
import sys
import tkinter as tk
from tkinter import filedialog
from controller import application
from gui import *
import tkinter.ttk as ttk
import random  # Testing

node_info = dict()


def get_random_number():
    point = random.randint(1, 500)
    return point


controller = application.Controller.get_instance()

filename = ''
scale = 1
dy = 0


def exit_window():
    # TODO popup save data, clean threads, ... (if exist)
    # controller.exit()
    destroy_window()
    sys.stdout.flush()


def save_popup_window():
    save_popup = tk.Tk()

    save_popup.geometry("230x100")
    save_popup.title("Save file...")

    x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
    y = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
    save_popup.geometry("+%d+%d" % (x, y))

    new_label = tk.Label(save_popup, text="Do you want to save this file?")
    new_label.place(relx=0.1, rely=0.1)
    new_label.configure(bg="#ffffff")

    yes_button = ttk.Button(save_popup, text="Yes", command=save_file_as)
    yes_button.place(relx=0.1, rely=0.5)

    def refresh_canvas():
        w.main_canvas.delete("all")
        save_popup.destroy()

    no_button = ttk.Button(save_popup, text="No", command=refresh_canvas)
    no_button.place(relx=0.5, rely=0.5)

    save_popup.mainloop()


def computer_popup_window():
    computer_popup = tk.Tk()

    computer_popup.geometry("500x1000")
    computer_popup.title("Node Properties")

    x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
    y = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
    computer_popup.geometry("+%d+%d" % (x, y))

    popup_label = tk.Label(computer_popup, text="This is node window properties")
    popup_label.place(relx=0.1, rely=0.1)
    popup_label.configure(bg="#ffffff")


def hub_popup_window():
    hub_popup = tk.Tk()

    hub_popup.geometry("500x1000")
    hub_popup.title("Node Properties")

    x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
    y = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
    hub_popup.geometry("+%d+%d" % (x, y))

    hub_label = tk.Label(hub_popup, text="This is hub window properties")
    hub_label.place(relx=0.1, rely=0.1)
    hub_label.configure(bg="#ffffff")


def modem_popup_window():
    modem_popup = tk.Tk()

    modem_popup.geometry("500x1000")
    modem_popup.title("Node Properties")

    x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
    y = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
    modem_popup.geometry("+%d+%d" % (x, y))

    modem_label = tk.Label(modem_popup, text="This is modem window properties")
    modem_label.place(relx=0.1, rely=0.1)
    modem_label.configure(bg="#ffffff")


def router_popup_window():
    router_popup = tk.Tk()

    router_popup.geometry("500x1000")
    router_popup.title("Node Properties")

    x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
    y = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
    router_popup.geometry("+%d+%d" % (x, y))

    router_label = tk.Label(router_popup, text="This is router window properties")
    router_label.place(relx=0.1, rely=0.1)
    router_label.configure(bg="#ffffff")


def switch_popup_window():
    switch_popup = tk.Tk()

    switch_popup.geometry("500x1000")
    switch_popup.title("Node Properties")

    x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
    y = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
    switch_popup.geometry("+%d+%d" % (x, y))

    switch_label = tk.Label(switch_popup, text="This is switch window properties")
    switch_label.place(relx=0.1, rely=0.1)
    switch_label.configure(bg="#ffffff")


def enable(child_list):
    # TODO fix this childList ??
    for child in childList:
        child.configure(state='enable')


def open_file():
    file = filedialog.askopenfile(
        title="Select file",
        filetypes=(("GraphML", "*.graphml"), ("Text file", "*.txt")))
    controller.load(file, w.main_canvas)
    controller.subscribe_inspection(update_node_info)
    controller.subscribe_coords(update_canvas_coords)
    sys.stdout.flush()


def create_new_file():
    save_popup_window()


def open_recent_file():
    print("Recent")


def save_file():
    global filename
    if filename == '':
        filename = filedialog.asksaveasfile(mode='w')
    if filename is not None:
        # TODO fix this ??
        data = textentry.get('1.0', 'end')
        filename.write(data)


def save_file_as():
    global filename
    filename = filedialog.asksaveasfile(mode='w')
    # TODO fix this ??
    file_save()
    '''
    file = filedialog.asksaveasfilename(
        initialdir="/", title="Select file",
        filetypes=(("jpeg files", "*.jpg"), ("Text files", "*.txt")))
    print(file, file.__class__)
    '''


def close():
    w.main_canvas.delete("all")
    for child in w.control_panel.winfo_children():
        if not isinstance(child, ttk.Separator):
            child.configure(state=tk.DISABLED)

    for child in w.data_panel.winfo_children():
        if not isinstance(child, ttk.Separator):
            child.configure(state=tk.DISABLED)


def undo():
    print("Undo")


def redo():
    print("Redo")


def zoom_in(event):
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
    if w.add_node_combobox.get() == "Computer":
        computer_popup_window()
    if w.add_node_combobox.get() == "Hub":
        hub_popup_window()
    if w.add_node_combobox.get() == "Modem":
        modem_popup_window()
    if w.add_node_combobox.get() == "Router":
        router_popup_window()
    if w.add_node_combobox.get() == "Switch":
        switch_popup_window()


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


def destroy_window():
    # Function which closes the window.
    global top_level
    top_level.destroy()
    top_level = None


def add_widget(type, text, relx):
    if type is "label":
        label = tk.Label(w.node_data_panel, text=text, font=("Helvetica", 12))
        label.configure(bg="#f0f0f0")
        label.place(relx=relx, rely=dy)
        return label
    elif type is "entry":
        entry = tk.Entry(w.node_data_panel, font=("Helvetica", 12))
        entry.insert(0, str(text))
        entry.place(relx=relx, rely=dy)
        return entry


def update_node_info(info):
    # print('Do something with this info', info)
    # clear the data panel
    global dy
    dy = 0
    node_info.clear()
    for widget in w.node_data_panel.winfo_children():
        widget.destroy()

    def add_node_info(key, value=None):
        global dy
        if value is not None:
            node_info[add_widget("label", key, 0.04)] = add_widget("entry", value, 0.5)
            dy += 0.09
        else:
            return add_widget("label", key, 0.04)

    def add_table_info(key, value):
        table_label = add_node_info(key)
        global dy
        dy += 0.09
        table_info = []
        for k, v in value.items():
            table_info.append([add_widget("entry", k, 0.04), add_widget("entry", v, 0.5)])
            dy += 0.09
        node_info[table_label] = table_info

    '''
    def add_edge_info(sub_info):
        nonlocal dy
        edge_data_label = tk.Label(w.edge_data_panel, text=sub_edge_info, font=("Helvetica", 12))
        edge_data_label.configure(bg="#f0f0f0")
        edge_data_label.place(relx=0.04, rely=dy)
        dy += 0.09
    '''

    for key, value in info.items():
        if isinstance(value, dict):
            add_table_info(key, value)
        else:
            add_node_info(key, value)


def node_modify():
    print("modifying")
    modify_info = dict()
    for key, value in node_info.items():
        if isinstance(value, list):
            table_info = dict()
            for a, b in value:
                table_info[a.get()] = b.get()
            modify_info[key['text']] = table_info
        else:
            modify_info[key['text']] = value.get()
    controller.modify(modify_info)


def update_canvas_coords(x, y):
    w.coordinate_x_label['text'] = str(x)
    w.coordinate_y_label['text'] = str(y)
