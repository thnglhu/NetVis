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


node_info_dict = dict()

node_info_dict_child = dict()

def node_properties_popup_window():
    node_popup = tk.Tk()

    node_popup.geometry("500x350")
    node_popup.title("Node Properties")

    x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
    y = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
    node_popup.geometry("+%d+%d" % (x, y))

    node_type_label = tk.Label(node_popup, text="Node Type:")
    node_type_label.place(relx=0.05, rely=0.03)
    node_type_label.configure(bg="#ffffff")

    box_value = StringVar()
    node_type_combobox = ttk.Combobox(node_popup, values=box_value)
    node_type_combobox['values'] = ('Host', 'Switch', 'Router')
    node_type_combobox.current(0)
    node_type_combobox.place(relx=0.5, rely=0.03)

    node_name_label = tk.Label(node_popup, text="Node Name:")
    node_name_label.place(relx=0.05, rely=0.1)
    node_name_label.configure(bg="#ffffff")

    node_name_textbox = tk.Entry(node_popup)
    node_name_textbox.place(relx=0.5, rely=0.1)
    node_name_textbox.configure(bg="#efefef")

    node_interface_label = tk.Label(node_popup, text="Node Interface:")
    node_interface_label.place(relx=0.05, rely=0.17)
    node_interface_label.configure(bg="#ffffff")

    ipaddress_interface_label = tk.Label(node_popup, text="Node IP Address:")
    ipaddress_interface_label.place(relx=0.1, rely=0.24)
    ipaddress_interface_label.configure(bg="#ffffff")

    ipaddress_interface_textbox = tk.Entry(node_popup)
    ipaddress_interface_textbox.place(relx=0.5, rely=0.24)
    ipaddress_interface_textbox.configure(bg="#efefef")

    ipnetwork_interface_label = tk.Label(node_popup, text="Node IP Network:")
    ipnetwork_interface_label.place(relx=0.1, rely=0.31)
    ipnetwork_interface_label.configure(bg="#ffffff")

    ipnetwork_interface_textbox = tk.Entry(node_popup)
    ipnetwork_interface_textbox.place(relx=0.5, rely=0.31)
    ipnetwork_interface_textbox.configure(bg="#efefef")

    default_gateway_interface_label = tk.Label(node_popup, text="Node Default Gateway:")
    default_gateway_interface_label.place(relx=0.1, rely=0.38)
    default_gateway_interface_label.configure(bg="#ffffff")

    default_gateway_interface_textbox = tk.Entry(node_popup)
    default_gateway_interface_textbox.place(relx=0.5, rely=0.38)
    default_gateway_interface_textbox.configure(bg="#efefef")

    def node_info_passing():
        node_info_dict.clear()
        node_info_dict["type"] = node_type_combobox.get()
        node_info_dict["name"] = node_name_textbox.get()
        node_info_dict["interface"] = node_info_dict_child
        node_info_dict_child["ip_addess"] = ipaddress_interface_textbox.get()
        node_info_dict_child["ip_network"] = ipnetwork_interface_textbox.get()
        node_info_dict_child["default_gateway"] = default_gateway_interface_textbox.get()
        print(node_info_dict)
        controller.create(node_info_dict)
        node_popup.destroy()

    node_button = tk.Button(node_popup, text="Apply", command=node_info_passing)
    node_button.place(relx=0.75, rely=0.5)





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


def zoom_in():
    w.main_canvas.scale("all", 450, 450, 1.1, 1.1)


def zoom_out():
    w.main_canvas.scale("all", 450, 450, 0.9, 0.9)


def find_node():
    print("Find node")


def cut():
    print("Cut")


def copy():
    print("Copy")


def paste():
    print("Paste")


def select_all():
    print("select all")


def select_all_nodes():
    print("Select All Nodes")


def deselect_all_nodes():
    print("Deselect All Nodes")


def add_node():
    node_properties_popup_window()


def remove_node():
    pass


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


node_info = dict()


def update_node_info(info):
    print('Do something with this info', info)
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
            dy += 0.1
        else:
            return add_widget("label", key, 0.04)

    def add_table_info(key, value):
        table_label = add_node_info(key)
        global dy
        dy += 0.09
        table_info = []
        for k, v in value.items():
            table_info.append([add_widget("entry", k, 0.04), add_widget("entry", v, 0.5)])
            dy += 0.15
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
