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
from support import device_addition_forms, info_forms

existed = False

node_info = dict()
node_info_dict = dict()
node_info_dict_child = dict()
router_interface_dict_child = dict()
arp_table_dict_child = dict()

controller = application.Controller.get_instance()

filename = ''
scale = 1
dy = 0
num = 0


def init(top, gui, *args, **kwargs):
    global w, top_level, root, x, y
    w = gui
    top_level = top
    root = top
    style = ttk.Style(root)
    style.configure('Treeview', rowheight=15)
    controller.init(w.main_canvas)


def open_file():
    file = filedialog.askopenfile(
        title="Select file",
        filetypes=(("JSON", "*.json"), )
    )
    if file:
        global existed
        controller.load_file(file)
        controller.subscribe_inspection(update_node_info)
        controller.subscribe_coords(update_canvas_coords)
        controller.subscribe_property(context_menu)
        existed = True
    sys.stdout.flush()


def save_file():
    if existed:
        file = filedialog.asksaveasfile(
            title='Save file as ...',
            defaultextension='.json',
            filetypes=(("JSON", "*.json"),)
        )
        if file:
            controller.save_file(file)
    sys.stdout.flush()


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

    yes_button = ttk.Button(save_popup, text="Yes", command=save_file)
    yes_button.place(relx=0.1, rely=0.5)

    def refresh_canvas():
        controller.clear()
        save_popup.destroy()

    no_button = ttk.Button(save_popup, text="No", command=refresh_canvas)
    no_button.place(relx=0.5, rely=0.5)

    save_popup.mainloop()


class node_properties_popup_window():

    def create_node_type(self):
        self.node_type_label = tk.Label(self.node_popup, text="Type:")
        self.node_type_label.place(relx=0.05, rely=0.03)
        self.node_type_label.configure(bg="#ffffff")

        self.box_value = StringVar()
        self.node_type_combobox = ttk.Combobox(self.node_popup, values=self.box_value)
        self.node_type_combobox['values'] = ('Host', 'Switch', 'Router')
        self.node_type_combobox.current(0)
        self.node_type_combobox.place(relx=0.5, rely=0.03)

    def create_node_name(self):
        self.node_name_label = tk.Label(self.node_popup_frame, text="Name:")
        self.node_name_label.place(relx=0.02, rely=0.01)
        self.node_name_label.configure(bg="#ffffff")

        self.node_name_textbox = tk.Entry(self.node_popup_frame)
        self.node_name_textbox.place(relx=0.5, rely=0.01)
        self.node_name_textbox.configure(bg="#efefef")

    def create_node_interface(self):
        self.node_interface_label = tk.Label(self.node_popup_frame, text="Interface name:")
        self.node_interface_label.place(relx=0.02, rely=0.09)
        self.node_interface_label.configure(bg="#ffffff")

        self.node_interface_textbox = tk.Entry(self.node_popup_frame)
        self.node_interface_textbox.place(relx=0.5, rely=0.09)
        self.node_interface_textbox.configure(bg="#efefef")

        self.ipaddress_interface_label = tk.Label(self.node_popup_frame, text="Interface IP address:")
        self.ipaddress_interface_label.place(relx=0.02, rely=0.17)
        self.ipaddress_interface_label.configure(bg="#ffffff")

        self.ipaddress_interface_textbox = tk.Entry(self.node_popup_frame)
        self.ipaddress_interface_textbox.place(relx=0.5, rely=0.17)
        self.ipaddress_interface_textbox.configure(bg="#efefef")

        self.ipnetwork_interface_label = tk.Label(self.node_popup_frame, text="Interface IP network:")
        self.ipnetwork_interface_label.place(relx=0.02, rely=0.26)
        self.ipnetwork_interface_label.configure(bg="#ffffff")

        self.ipnetwork_interface_textbox = tk.Entry(self.node_popup_frame)
        self.ipnetwork_interface_textbox.place(relx=0.5, rely=0.26)
        self.ipnetwork_interface_textbox.configure(bg="#efefef")

        self.default_gateway_interface_label = tk.Label(self.node_popup_frame, text="Interface default gateway:")
        self.default_gateway_interface_label.place(relx=0.02, rely=0.34)
        self.default_gateway_interface_label.configure(bg="#ffffff")

        self.default_gateway_interface_textbox = tk.Entry(self.node_popup_frame)
        self.default_gateway_interface_textbox.place(relx=0.5, rely=0.34)
        self.default_gateway_interface_textbox.configure(bg="#efefef")

    def create_router_interface_table(self):
        def add_interface():
            global num
            num = 0
            while num in router_interface_dict_child:
                num += 1
            else:
                router_interface_dict_child[num] = self.router_interface_textbox.get()
            self.router_interface_textbox.delete('0', tk.END)

        self.interface_label = tk.Label(self.node_popup_frame, text="Router Interface:")
        self.interface_label.place(relx=0.02, rely=0.09)
        self.interface_label.configure(bg="#ffffff")

        self.router_interface_textbox = tk.Entry(self.node_popup_frame)
        self.router_interface_textbox.place(relx=0.5, rely=0.09)
        self.router_interface_textbox.configure(bg="#efefef")

        self.router_interface_button = tk.Button(self.node_popup_frame, text="+", command=add_interface)
        self.router_interface_button.place(relx=0.87, rely=0.09)

    def create_arp_table(self):
        def add_arp():
            global num
            num = 0
            while num in arp_table_dict_child:
                num += 1
            else:
                arp_table_dict_child[num] = self.arp_textbox.get()
            self.arp_textbox.delete('0', tk.END)

        self.arp_label = tk.Label(self.node_popup_frame, text="Static ARP table:")
        self.arp_label.place(relx=0.02, rely=0.42)
        self.arp_label.configure(bg="#ffffff")

        self.arp_textbox = tk.Entry(self.node_popup_frame)
        self.arp_textbox.place(relx=0.5, rely=0.42)
        self.arp_textbox.configure(bg="#efefef")

        self.arp_button = tk.Button(self.node_popup_frame, text="+", command=add_arp)
        self.arp_button.place(relx=0.87, rely=0.42)

    def create_router_arp_table(self):
        def add_router_arp():
            global num
            num = 0
            while num in arp_table_dict_child:
                num += 1
            else:
                arp_table_dict_child[num] = self.router_arp_textbox.get()
            self.router_arp_textbox.delete('0', tk.END)

        self.arp_label = tk.Label(self.node_popup_frame, text="Static ARP table:")
        self.arp_label.place(relx=0.02, rely=0.17)
        self.arp_label.configure(bg="#ffffff")

        self.router_arp_textbox = tk.Entry(self.node_popup_frame)
        self.router_arp_textbox.place(relx=0.5, rely=0.17)
        self.router_arp_textbox.configure(bg="#efefef")

        self.router_arp_button = tk.Button(self.node_popup_frame, text="+", command=add_router_arp)
        self.router_arp_button.place(relx=0.87, rely=0.173)

    def create_mac_table(self):
        def add_mac():
            global num
            num = 0
            while num in node_info_dict_child:
                num += 1
            else:
                node_info_dict_child[num] = self.mac_textbox.get()
            self.mac_textbox.delete('0', tk.END)

        self.mac_label = tk.Label(self.node_popup_frame, text="Static MAC table:")
        self.mac_label.place(relx=0.02, rely=0.09)
        self.mac_label.configure(bg="#ffffff")

        self.mac_textbox = tk.Entry(self.node_popup_frame)
        self.mac_textbox.place(relx=0.5, rely=0.09)
        self.mac_textbox.configure(bg="#efefef")

        self.mac_button = tk.Button(self.node_popup_frame, text="+", command=add_mac)
        self.mac_button.place(relx=0.87, rely=0.09)

    def create_routing_table(self):

        def add_routing():
            node_info_dict_child[self.routing_address_textbox.get()] = self.routing_interface_textbox.get()
            self.routing_address_textbox.delete('0', tk.END)
            self.routing_interface_textbox.delete('0', tk.END)

        self.routing_label = tk.Label(self.node_popup_frame, text="Static routing Table: ")
        self.routing_label.place(relx=0.02, rely=0.25)
        self.routing_label.configure(bg="#ffffff")

        self.routing_ipv4_address = tk.Label(self.node_popup_frame, text="IP address: ")
        self.routing_ipv4_address.place(relx=0.025, rely=0.33)
        self.routing_ipv4_address.configure(bg="#ffffff")

        self.routing_address_textbox = tk.Entry(self.node_popup_frame)
        self.routing_address_textbox.place(relx=0.23, rely=0.33)
        self.routing_address_textbox.configure(bg="#efefef", width=15)

        self.routing_interface_address = tk.Label(self.node_popup_frame, text="Interface name")
        self.routing_interface_address.place(relx=0.51, rely=0.33)
        self.routing_interface_address.configure(bg="#ffffff")

        self.routing_interface_textbox = tk.Entry(self.node_popup_frame)
        self.routing_interface_textbox.place(relx=0.65, rely=0.33)
        self.routing_interface_textbox.configure(bg="#efefef", width=14)

        self.routing_button = tk.Button(self.node_popup_frame, text="+", command=add_routing)
        self.routing_button.place(relx=0.92, rely=0.33)

    def node_info_passing(self):

        node_info_dict["type"] = self.node_type_combobox.get()
        node_info_dict["name"] = self.node_name_textbox.get()

        if self.node_type_combobox.get() == "Host":
            node_info_dict["interface"] = node_info_dict_child
            node_info_dict_child["name"] = self.node_interface_textbox.get()
            node_info_dict_child["ip_address"] = self.ipaddress_interface_textbox.get()
            node_info_dict_child["ip_network"] = self.ipnetwork_interface_textbox.get()
            node_info_dict_child["default_gateway"] = self.default_gateway_interface_textbox.get()
            node_info_dict["arp table"] = arp_table_dict_child
            print(node_info_dict)
            node_info_dict.clear()
            node_info_dict_child.clear()
            arp_table_dict_child.clear()
        elif self.node_type_combobox.get() == "Switch":
            node_info_dict["mac table"] = node_info_dict_child
            print(node_info_dict)
            node_info_dict.clear()
            node_info_dict_child.clear()
        elif self.node_type_combobox.get() == "Router":
            node_info_dict["arp table"] = arp_table_dict_child
            node_info_dict["interface"] = router_interface_dict_child
            node_info_dict["routing table"] = node_info_dict_child
            print(node_info_dict)
            node_info_dict.clear()
            node_info_dict_child.clear()
            arp_table_dict_child.clear()
            router_interface_dict_child.clear()

        # controller.create(node_info_dict)
        self.node_popup.destroy()

    def draw(self, event):
        if self.node_type_combobox.get() == "Host":
            for child in self.node_popup_frame.winfo_children():
                child.destroy()
            self.create_node_name()
            self.create_node_interface()
            self.create_arp_table()
            self.apply_button()

        elif self.node_type_combobox.get() == "Switch":
            for child in self.node_popup_frame.winfo_children():
                child.destroy()
            self.create_node_name()
            self.create_mac_table()
            self.apply_button()

        elif self.node_type_combobox.get() == "Router":
            for child in self.node_popup_frame.winfo_children():
                child.destroy()
            self.create_node_name()
            self.create_router_interface_table()
            self.create_router_arp_table()
            self.create_routing_table()
            self.apply_button()

    def apply_button(self):
        self.node_button = tk.Button(self.node_popup_frame, text="Apply", command=self.node_info_passing)
        self.node_button.place(relx=0.70, rely=0.55)

    def __init__(self):
        '''
        self.router_arp_textbox = None
        self.mac_textbox = None
        self.arp_textbox = None
        self.ipaddress_interface_textbox = None
        self.ipnetwork_interface_textbox = None
        self.default_gateway_interface_textbox = None
        self.node_interface_textbox = None
        '''
        self.node_popup = tk.Tk()

        self.node_popup_frame = tk.Frame(self.node_popup)
        self.node_popup_frame.place(relx=0.05, rely=0.1)
        self.node_popup_frame.configure(width=470, height=300, bg="#fafafa")

        self.node_popup.geometry("500x350")
        self.node_popup.title("Node Properties")

        x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
        y = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
        self.node_popup.geometry("+%d+%d" % (x, y))

        self.create_node_type()

        self.node_type_combobox.bind('<<ComboboxSelected>>', self.draw)

def enable(child_list):
    # TODO fix this childList ??
    for child in childList:
        child.configure(state='enable')


def create_new_file():
    save_popup_window()


def open_recent_file():
    print("Recent")


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
    w.main_canvas.scale("all", 450, 450, 0.9, 0.9)


def zoom_out():
    w.main_canvas.scale("all", 450, 450, 1.1, 1.1)


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
    if existed:
        windows = tk.Tk()
        parent = ttk.Notebook(windows)
        host_tab = ttk.Frame(parent)
        device_addition_forms.HostForm(host_tab, controller.create)
        switch_tab = ttk.Frame(parent)
        device_addition_forms.SwitchForm(switch_tab, controller.create)
        router_tab = ttk.Frame(parent)
        router_tab.columnconfigure(0, weight=1)
        device_addition_forms.RouterForm(router_tab, controller.create)
        parent.add(host_tab, text="Host")
        parent.add(switch_tab, text="Switch")
        parent.add(router_tab, text="Router")
        parent.pack(expand=1, fill='both')
    # node_properties_popup_window()


def motion(event):
    x, y = event.x, event.y
    print('{}, {}'.format(x, y))


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


def destroy_window():
    # Function which closes the window.
    global top_level
    top_level.destroy()
    top_level = None


def add_widget(type, text, relx, **kwargs):
    if type is "label":
        label = tk.Label(w.node_data_panel, text=text, font=("Helvetica", 12), state=kwargs.get('state'))
        label.configure(bg="#f0f0f0")
        label.place(relx=relx, rely=dy)
        return label
    elif type is "entry":
        entry = tk.Entry(w.node_data_panel, font=("Helvetica", 12), state=kwargs.get('state'))
        if text is not None:
            entry.insert(0, str(text))
        entry.place(relx=relx, rely=dy)
        return entry


def update_log(log):
    w.log_text['state'] = 'normal'
    w.log_text.insert('1.0', '\n\n')
    w.log_text.insert('1.0', log)
    w.log_text['state'] = 'disabled'


def update_node_info(info):
    for widget in w.node_data_panel.winfo_children():
        widget.destroy()
    from support import extension as ex
    frame = ex.VerticalScrollable(w.node_data_panel)
    print(info['type'])
    if info['type'] == 'host':
        info_forms.HostInfo(frame, info, node_modify)
    elif info['type'] == 'switch':
        info_forms.SwitchInfo(frame, info, node_modify)
    elif info['type'] == 'router':
        info_forms.RouterInfo(frame, info, node_modify)
    pass
    frame.update()
    """
    # print('Do something with this info', info)
    # update_log(info)
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

    for key, value in info.items():
        if value[0]:
            if isinstance(value[1], dict):
                add_table_info(key, value[1])
            else:
                add_node_info(key, value[1])
"""


def node_modify(info):
    if existed:
        controller.modify_device(info)


def context_menu(info):
    menu = tk.Menu(w.main_canvas, tearoff=0)
    menu_dictionary = {
        'host': {
            'Connect': controller.prepare_connecting,
            'Send to': controller.send_message,
            'Disable': controller.disable_device,
        },
        'switch': {
            'Connect': controller.prepare_connecting,
            'Disable': controller.disable_device,
        },
        'router': {
            'Connect': router_connect,
            'Add an interface': add_interface,
            'Disable': controller.disable_device,
        }
    }
    if info['type'] not in menu_dictionary:
        raise KeyError
    from functools import partial
    for text, function in menu_dictionary[info['type']].items():
        menu.add_command(label=text, command=partial(function, info) if function is not None else None)

    try:
        _x = root.winfo_pointerx()
        _y = root.winfo_pointery()
        menu.tk_popup(_x, _y)
    finally:
        menu.grab_release()


def router_connect(info):
    select_interface_popup = tk.Tk()
    select_interface_popup.geometry("500x500")
    select_interface_popup.title("Select an Interface of Router " + info['type'])
    select_interface_popup.geometry("+%d+%d" % (
    (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2, (root.winfo_screenheight() - root.winfo_reqheight()) / 2))

    # Combo box handling
    interfaces_combobox = ttk.Combobox(select_interface_popup, values=[])
    interfaces_combobox.place(relx=0.02, rely=0.02)
    print(info)
    for interface in map(lambda each: each['name'], info['interfaces']):
        interfaces_combobox['values'] += (interface,)
    interfaces_combobox.current(0)

    # OK & Cancel buttons
    def close_popup():
        select_interface_popup.destroy()

    def select_interface():
        controller.select_interface(interfaces_combobox.get())
        close_popup()

    ok_button = tk.Button(select_interface_popup, text="OK", command=select_interface)
    ok_button.pack(side='bottom')
    cancel_button = tk.Button(select_interface_popup, text="Cancel", command=close_popup)
    cancel_button.pack(side='bottom')


def add_interface(info):
    if info['type'] != "router":
        return

    add_interface_popup = tk.Tk()
    add_interface_popup.geometry("500x500")
    add_interface_popup.title("Add New Interface to Router: " + info['name'])
    add_interface_popup.geometry("+%d+%d" % (
    (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2, (root.winfo_screenheight() - root.winfo_reqheight()) / 2))

    # TODO: do not accept duplicate name
    global dy
    dy = 0.02
    # INPUT

    dy += 0.1
    label = tk.Label(add_interface_popup, text="Interface Name: ", font=("Helvetica", 12))
    label.configure(bg="#f0f0f0")
    label.place(relx=0.02, rely=dy)
    ifname_input = tk.Entry(add_interface_popup, font=("Helvetica", 12))
    ifname_input.place(relx=0.5, rely=dy)

    dy += 0.1
    label = tk.Label(add_interface_popup, text="Mac Address: ", font=("Helvetica", 12))
    label.configure(bg="#f0f0f0")
    label.place(relx=0.02, rely=dy)
    ifmac_input = tk.Entry(add_interface_popup, font=("Helvetica", 12))
    ifmac_input.place(relx=0.5, rely=dy)
    ifmac_input.insert(0, 'ff.ff.ff.ff.ff.ff')

    dy += 0.1
    label = tk.Label(add_interface_popup, text="IP Address: ", font=("Helvetica", 12))
    label.configure(bg="#f0f0f0")
    label.place(relx=0.02, rely=dy)
    ifaddress_input = tk.Entry(add_interface_popup, font=("Helvetica", 12))
    ifaddress_input.place(relx=0.5, rely=dy)
    ifaddress_input.insert(0, '0.0.0.0')

    dy += 0.1
    label = tk.Label(add_interface_popup, text="IP Network: ", font=("Helvetica", 12))
    label.configure(bg="#f0f0f0")
    label.place(relx=0.02, rely=dy)
    ifnet_input = tk.Entry(add_interface_popup, font=("Helvetica", 12))
    ifnet_input.place(relx=0.5, rely=dy)
    ifnet_input.insert(0, '0.0.0.0/24')

    dy += 0.1
    label = tk.Label(add_interface_popup, text="Default Gateway: ", font=("Helvetica", 12))
    label.configure(bg="#f0f0f0")
    label.place(relx=0.02, rely=dy)
    gateway_input = tk.Entry(add_interface_popup, font=("Helvetica", 12), text='ASDasdasd')
    gateway_input.place(relx=0.5, rely=dy)
    gateway_input.insert(0, '0.0.0.0')

    # OK & CANCEL BUTTONS
    def close_popup():
        add_interface_popup.destroy()

    def create_interface():
        interface_info = dict()
        interface_info['name'] = ifname_input.get()
        interface_info['mac_address'] = ifmac_input.get()
        interface_info['ip_address'] = ifaddress_input.get()
        interface_info['ip_network'] = ifnet_input.get()
        interface_info['default_gateway'] = gateway_input.get()
        controller.add_interface(interface_info)
        close_popup()

    ok_button = tk.Button(add_interface_popup, text="OK", command=create_interface)
    ok_button.pack(side='bottom')
    cancel_button = tk.Button(add_interface_popup, text="Cancel", command=close_popup)
    cancel_button.pack(side='bottom')


def update_canvas_coords(x, y):
    w.coordinate_x_label['text'] = str(x)
    w.coordinate_y_label['text'] = str(y)

