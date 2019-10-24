import tkinter
from tkinter import ttk
from ..Extension import VerticalScrollable
from random import randint
from functools import partial
from .info_form import InfoForm


class AdditionForm:

    def __init__(self, root, graph):
        self.graph = graph
        self.all_data = list()
        self.data = None
        self.info = None
        self.special = 0
        root.bind('<Escape>', self.cancel)

    def load_form(self):
        data = self.data = dict()
        self.all_data.append(data)
        data['form'] = tkinter.Toplevel()
        data['form'].title('Add device')
        data['form'].geometry("380x512")
        data['note'] = ttk.Notebook(data['form'])
        host_tab = tkinter.Frame(data['note'])
        hub_tab = tkinter.Frame(data['note'])
        router_tab = tkinter.Frame(data['note'])

        host_frame = VerticalScrollable(host_tab)
        self.__prepare_host(data, host_frame)
        host_frame.update()
        hub_frame = VerticalScrollable(hub_tab)
        self.__prepare_hub(data, hub_frame)
        hub_frame.update()
        router_frame = VerticalScrollable(router_tab)
        self.__prepare_router(data, router_frame)
        router_frame.update()

        data['note'].add(host_tab, text="Host")
        data['note'].add(hub_tab, text="Hub/Switch")
        data['note'].add(router_tab, text="Router")
        data['note'].pack(fill=tkinter.BOTH, expand=1)

    def add_device(self, device_type):
        translate = {
            'host': 0,
            'hub': 1,
            'switch': 1,
            'router': 2
        }
        if device_type == 'switch':
            self.special = 1
        else:
            self.special = 0
        self.load_form()
        self.data['note'].select(translate[device_type])
        self.data['form'].focus_force()

    def load(self, x, y):
        if self.info:
            self.info['position'] = self.graph.canvas.invert_position(x, y)
            self.graph.add_device(self.info)
            self.info = None

    def __prepare_host(self, data, host_frame):
        tkinter.Label(host_frame, text="Name: ").grid(row=0, column=0, sticky="W")

        name = tkinter.Entry(host_frame)
        name.grid(row=0, column=1, sticky="W")

        tkinter.Label(host_frame, text="Default gateway: ").grid(row=1, column=0, sticky="W")

        default_gateway = tkinter.Entry(host_frame)
        default_gateway.grid(row=1, column=1, sticky="W")

        tkinter.Label(host_frame, text="Interface: ").grid(row=2, column=0, sticky="W")

        tkinter.Label(host_frame, text="Port name: ").grid(row=3, column=0, padx=10, sticky="W")

        port_name = tkinter.Entry(host_frame)
        port_name.grid(row=3, column=1, sticky="W")
        port_name.insert(0, "eth0")

        tkinter.Label(host_frame, text="Mac Address: ").grid(row=4, column=0, padx=10, sticky="W")

        mac_address = tkinter.Entry(host_frame)
        mac_address.grid(row=4, column=1, sticky="W")

        def random_mac_address():
            mac_address.delete(0, tkinter.END)
            mac_address.insert(0, "%02x:%02x:%02x:%02x:%02x:%02x" % (
                randint(0, 255), randint(0, 255), randint(0, 255), randint(0, 255), randint(0, 255), randint(0, 255)
            ))
        tkinter.Button(host_frame, text="Re-roll", command=random_mac_address).grid(row=4, column=2, sticky="W")
        random_mac_address()

        tkinter.Label(host_frame, text="IP Interface: ").grid(row=5, column=0, padx=10, sticky="W")

        ip_interface = tkinter.Entry(host_frame)
        ip_interface.grid(row=5, column=1, sticky="W")

        def submit():
            self.info = {
                'type': 'host',
                'name': name.get(),
                'default_gateway': default_gateway.get(),
                'status': True,
                'interface': {
                    'mac_address': mac_address.get(),
                    'ip_interface': ip_interface.get(),
                    'port': {
                        'name': port_name.get(),
                    },
                },
            }
            self.all_data.remove(data)
            data['form'].destroy()

        tkinter.Button(host_frame, text="Submit", command=submit).grid(row=6, column=2, sticky="E")

    def __prepare_hub(self, data, hub_frame):
        tkinter.Label(hub_frame, text="Type: ").grid(row=0, column=0, sticky="W")

        _type = ttk.Combobox(hub_frame, values=['hub', 'switch'], state="readonly")
        _type.grid(row=0, column=1, sticky="W")
        _type.current(0 if not hasattr(self, 'special') else getattr(self, 'special'))

        tkinter.Label(hub_frame, text="Name: ").grid(row=1, column=0, sticky="W")

        name = tkinter.Entry(hub_frame)
        name.grid(row=1, column=1, sticky="W")

        tkinter.Label(hub_frame, text="Mac Address: ").grid(row=2, column=0, sticky="W")

        mac_address = tkinter.Entry(hub_frame)
        mac_address.grid(row=2, column=1, sticky="W")

        def random_mac_address():
            mac_address.delete(0, tkinter.END)
            mac_address.insert(0, "%02x:%02x:%02x:%02x:%02x:%02x" % (
                randint(0, 255), randint(0, 255), randint(0, 255), randint(0, 255), randint(0, 255), randint(0, 255)
            ))

        tkinter.Button(hub_frame, text="Re-roll", command=random_mac_address).grid(row=2, column=2, sticky="W")
        random_mac_address()

        tkinter.Label(hub_frame, text="Number of ports: ").grid(row=3, column=0, sticky="W")

        port_number = ttk.Spinbox(hub_frame, from_=1, to=10, state="readonly")

        list_box = tkinter.Listbox(hub_frame)

        def spin_box_change(increment, _):
            if increment:
                if int(port_number.get()) < 10:
                    list_box.insert(tkinter.END, "fa0/%s %02x:%02x:%02x:%02x:%02x:%02x" % (port_number.get(), randint(0, 255), randint(0, 255), randint(0, 255), randint(0, 255), randint(0, 255), randint(0, 255)))
            else:
                if int(port_number.get()) > 0:
                    list_box.delete(int(port_number.get()) - 1, tkinter.END)

        port_number.grid(row=3, column=1, sticky="W")
        port_number.set(1)
        port_number.bind("<<Increment>>", partial(spin_box_change, True))
        port_number.bind("<<Decrement>>", partial(spin_box_change, False))

        list_box.grid(row=4, column=1, sticky="W")
        list_box.insert(tkinter.END, "fa0/0 %02x:%02x:%02x:%02x:%02x:%02x" % (randint(0, 255), randint(0, 255), randint(0, 255), randint(0, 255), randint(0, 255), randint(0, 255)))

        def submit():
            self.info = {
                'type': _type.get(),
                'name': name.get(),
                'mac_address': mac_address.get(),
                'status': True,
                'ports': [
                    {
                        "name": string.split(' ')[0],
                        "mac_address": string.split(' ')[1]
                    } for string in list_box.get(0, tkinter.END)
                ],
            }
            self.all_data.remove(data)
            data['form'].destroy()

        tkinter.Button(hub_frame, text="Submit", command=submit).grid(row=5, column=2, sticky="E")

    def __prepare_router(self, data, router_frame):
        tkinter.Label(router_frame, text='Name: ').grid(row=0, column=0, sticky="W")

        name = tkinter.Entry(router_frame)
        name.grid(row=0, column=1, sticky="W")

        tkinter.Label(router_frame, text='Interfaces').grid(row=1, column=0, sticky="W")

        interface_treeview = InfoForm.tree_view(router_frame, ['Interface', 'MAC Address', 'IP Interface'], True)
        interface_treeview.grid(row=2, column=0, columnspan=4, sticky="W")

        tkinter.Label(router_frame, text='Interfaces: ').grid(row=3, column=0, sticky="W")
        tkinter.Label(router_frame, text='Port Name: ').grid(row=4, column=0, sticky="W", padx=10)
        tkinter.Label(router_frame, text='MAC Address: ').grid(row=5, column=0, sticky="W", padx=10)
        tkinter.Label(router_frame, text='IP Interface: ').grid(row=6, column=0, sticky="W", padx=10)

        port_name = tkinter.Entry(router_frame)
        port_name.grid(row=4, column=1, sticky="W")

        mac_address = tkinter.Entry(router_frame)
        mac_address.grid(row=5, column=1, sticky="W")

        ip_interface = tkinter.Entry(router_frame)
        ip_interface.grid(row=6, column=1, sticky="W")

        def random_mac_address():
            mac_address.delete(0, tkinter.END)
            mac_address.insert(0, "%02x:%02x:%02x:%02x:%02x:%02x" % (
                randint(0, 255), randint(0, 255), randint(0, 255), randint(0, 255), randint(0, 255), randint(0, 255)
            ))

        tkinter.Button(router_frame, text="Re-roll", command=random_mac_address).grid(row=5, column=2, sticky="W")
        random_mac_address()

        def add_interface():
            InfoForm.insert_treeview(interface_treeview, [
                port_name.get(),
                mac_address.get(),
                ip_interface.get(),
            ])
            port_name.delete(0, tkinter.END)
            ip_interface.delete(0, tkinter.END)
            random_mac_address()

        tkinter.Button(router_frame, text='Add', command=add_interface).grid(row=7, column=2, sticky="W")

        tkinter.Label(router_frame, text='Static Routing Table: ').grid(row=8, column=0, sticky="W")

        forward_treeview = InfoForm.tree_view(router_frame, ['Network', 'Next Hop', 'Interface'], True)
        forward_treeview.grid(row=9, column=0, columnspan=4, sticky="W")

        tkinter.Label(router_frame, text='Rule: ').grid(row=10, column=0, sticky="W")
        tkinter.Label(router_frame, text='Network: ').grid(row=11, column=0, sticky="W", padx=10)
        tkinter.Label(router_frame, text='Next Hop: ').grid(row=12, column=0, sticky="W", padx=10)
        tkinter.Label(router_frame, text='Interface: ').grid(row=13, column=0, sticky="W", padx=10)

        network = tkinter.Entry(router_frame)
        network.grid(row=11, column=1, sticky="W")

        next_hop = tkinter.Entry(router_frame)
        next_hop.grid(row=12, column=1, sticky="W")

        interface = tkinter.Entry(router_frame)
        interface.grid(row=13, column=1, sticky="W")

        def add_rule():
            InfoForm.insert_treeview(forward_treeview, [
                network.get(),
                next_hop.get(),
                interface.get(),
            ])
            network.delete(0, tkinter.END)
            next_hop.delete(0, tkinter.END)
            interface.delete(0, tkinter.END)

        tkinter.Button(router_frame, text='Add', command=add_rule).grid(row=14, column=2, sticky="W")

        def submit():
            self.info = {
                'type': 'router',
                'name': name.get(),
                'status': True,
                'interfaces': [
                    {
                        'mac_address': _interface[1],
                        'ip_interface': _interface[2],
                        'port': {
                            'name': _interface[0]
                        }
                    } for _interface in InfoForm.get_treeview(interface_treeview)
                ],
                'static_routing_table': [
                    {
                        'network': rule[0],
                        'next_hop': rule[1],
                        'interface': rule[2]
                    } for rule in InfoForm.get_treeview(forward_treeview)
                ]
            }
            self.all_data.remove(data)
            data['form'].destroy()

        tkinter.Button(router_frame, text='Submit', command=submit).grid(row=15, column=2, sticky="E")

    def cancel(self, _):
        if self.info:
            self.info = None
