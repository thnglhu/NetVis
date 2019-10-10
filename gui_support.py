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
    global w, top_level, root, x, y, existed
    w = gui
    top_level = top
    root = top
    style = ttk.Style(root)
    style.configure('Treeview', rowheight=15)
    controller.init(w.main_canvas)
    controller.subscribe_inspection(update_node_info)
    controller.subscribe_coords(update_canvas_coords)
    controller.subscribe_property(context_menu)
    existed = True
    setup_filter()


def open_file():
    file = filedialog.askopenfile(
        title="Select file",
        filetypes=(("JSON", "*.json"), )
    )
    if file:
        controller.load_file(file)
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

def create_new_file():
    save_popup_window()


def open_recent_file():
    print("Recent")


def close():
    w.main_canvas.delete("all")
    for child in w.control_panel.winfo_children():
        if not isinstance(child, ttk.Separator):
            child.configure(state=tk.DISABLED)

    for child in w.data_panel.winfo_children():
        if not isinstance(child, ttk.Separator):
            child.configure(state=tk.DISABLED)

def zoom_in():
    w.main_canvas.zoom((450, 450), potential=1/1.2)


def zoom_out():
    w.main_canvas.zoom((450, 450), potential=1.2)


def find_device(*args):
    print(args)
    controller.find_device(w.search_box.get())

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
        windows.lift()
    # node_properties_popup_window()


def remove_node():
    controller.delete()
    pass



def motion(event):
    x, y = event.x, event.y
    print('{}, {}'.format(x, y))


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
    print(info.get('name'), info.get('status'))
    frame = ex.HorizontalScrollable(w.node_data_panel)
    if info['type'] == 'host':
        info_forms.HostInfo(frame, info, node_modify)
    elif info['type'] == 'switch':
        info_forms.SwitchInfo(frame, info, node_modify)
    elif info['type'] == 'router':
        info_forms.RouterInfo(frame, info, node_modify)
    pass

    frame.update()

def setup_filter():
    from visual import visible
    from resource import get_image
    from functools import partial

    def switch(label, name, event):
        print("Hello")
        visible[name] ^= True
        _on = visible[name]
        _image = get_image(name if _on else name + '-off')
        label.configure(image=_image.get_image())

    count = 0
    for name, on in visible.items():
        image = get_image(name if on else name + '-off')
        label = tk.Label(w.filter_panel, image=image.get_image())
        label.grid(row=0, column=count)
        label.bind('<Button-1>', partial(switch, label, name))
        count += 1

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
            'Activate STP': controller.activate_stp,
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
    # select_interface_popup.geometry("500x500")
    select_interface_popup.title("Select an Interface of Router " + info['type'])
    select_interface_popup.geometry("+%d+%d" % (
    (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2, (root.winfo_screenheight() - root.winfo_reqheight()) / 2))

    # Combo box handling
    interfaces_combobox = ttk.Combobox(select_interface_popup, values=[])
    interfaces_combobox.grid(row=1, column=0, padx=10, pady=10, sticky="nesw")
    # interfaces_combobox.place(relx=0.02, rely=0.02)
    print(info)
    for interface in map(lambda each: each['name'], info['interfaces']):
        interfaces_combobox['values'] += (interface,)
    # interfaces_combobox.current(0)
    # interface info label
    info_label = tk.Label(select_interface_popup)
    info_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
    # info_label.configure(bg="#f0f0f0")
    # info_label.place(relx=0.02, rely=0.1)

    def update_info_label(event):
        current_interface = interfaces_combobox.get()
        for interface in info['interfaces']:
            if interface['name'] == current_interface:
                info_label['text'] = "MAC Address: " + interface['mac_address'] \
                                     + "\nIP Address: " + str(interface['ip_address']) \
                                     + "\nIP Network: " + str(interface['ip_network']) \
                                     + "\nDefault Gateway: " + str(interface['default_gateway'])
                break

    interfaces_combobox.bind("<<ComboboxSelected>>", update_info_label)
    # OK & Cancel buttons
    def close_popup():
        select_interface_popup.destroy()

    def select_interface():
        controller.select_interface(interfaces_combobox.get())
        close_popup()

    ok_button = tk.Button(select_interface_popup, text="OK", command=select_interface)
    ok_button.grid(row=3)
    # ok_button.pack(side='bottom')
    cancel_button = tk.Button(select_interface_popup, text="Cancel", command=close_popup)
    cancel_button.grid(row=4)
    # cancel_button.pack(side='bottom')


def add_interface(info):
    if info['type'] != "router":
        return
    print(info)
    add_interface_popup = tk.Tk()
    add_interface_popup.geometry("1000x500")
    add_interface_popup.configure(bg="#ffffff")
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

