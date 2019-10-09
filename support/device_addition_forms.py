import tkinter as tk
import tkinter.ttk as ttk
from . import Form
from functools import partial


class HostForm(Form):
    data = dict()
    instance = None

    def __init__(self, root, trigger):
        self.head = root
        self.trigger = trigger
        self.label(text="Name: ", row=0, column=1)
        self['name'] = self.entry(row=0, column=2)
        self.label(text="Interface: ", row=1, column=1)
        interface = self['interface'] = dict()
        self.label(text="Name: ", row=2, column=1, padx=15)
        interface['name'] = self.entry(row=2, column=2)
        self.label(text="MAC address: ", row=3, column=1, padx=15)
        interface['mac_address'] = self.entry(row=3, column=2)
        self.label(text="IP address: ", row=4, column=1, padx=15)
        interface['ip_address'] = self.entry(row=4, column=2)
        self.label(text="IP network: ", row=5, column=1, padx=15)
        interface['ip_network'] = self.entry(row=5, column=2)
        self.label(text="Default gateway: ", row=6, column=1, padx=15)
        interface['default_gateway'] = self.entry(row=6, column=2)
        self.exclusive()

    def exclusive(self):
        self.button(text="Submit", row=11, column=8, command=self.__trigger)

    def __trigger(self):
        print(self)
        self.trigger(self.get_info())

    def get_info(self):
        result = super().get_info()
        result['type'] = 'host'
        return result


class SwitchForm(Form):
    data = dict()
    def __init__(self, root, trigger):
        self.head = root
        self.trigger = trigger
        self.label(text="Name: ", row=0, column=1)
        self['name'] = self.entry(row=0, column=2)
        self.label(text="Mac address: ", row=1, column=1)
        self['mac_address'] = self.entry(row=1, column=2)
        self.exclusive()

    def exclusive(self):
        self.button(text="Submit", row=11, column=8, command=self.__trigger)

    def __trigger(self):
        print(self)
        self.trigger(self.get_info())

    def get_info(self):
        result = super().get_info()
        result['type'] = 'switch'
        return result


class RouterForm(Form):
    data = dict()

    def __init__(self, root, trigger):
        self.head = root
        self.trigger = trigger
        self.label(text="Name: ", row=0, column=1)
        self['name'] = self.entry(row=0, column=2)
        self['interfaces'] = self.tree_view(
            headers=("Name", "Mac address", "IP address", "IP network", "Default gateway"),
            row=3,
            column=0,
            columnspan=4,
            padx=10,
            sticky="we",
            stretch=0
        )

        self['routing_table'] = self.tree_view(
            headers=("Destination", "Next hop", "Interface", "Type"),
            row=3,
            column=5,
            columnspan=4,
            padx=10,
            sticky="we",
            stretch=0
        )
        self.label(text="Destination: ", row=4, column=5)
        routing_table = dict()
        routing_table['destination'] = self.entry(row=4, column=6, columnspan=3)
        self.label(text="Next hop: ", row=5, column=5)
        routing_table['next_hop'] = self.entry(row=5, column=6,columnspan=3)
        self.label(text="Interface: ", row=6, column=5)
        routing_table['interface'] = self.entry(row=6, column=6,columnspan=3)
        self.label(text="Type: ", row=7, column=5)
        routing_table['type'] = self.entry(row=7, column=6,columnspan=3)

        def add_rule():
            Form.tree_append(
                self['routing_table'],
                routing_table['destination'].get(),
                routing_table['next_hop'].get(),
                routing_table['interface'].get(),
                routing_table['type'].get()
            )
            Form.entry_set(routing_table['destination'], '')
            Form.entry_set(routing_table['next_hop'], '')
            Form.entry_set(routing_table['interface'], '')
            Form.entry_set(routing_table['type'], '')
        self.button(text="Append", row=8, sticky="es", column=8, command=add_rule)
        self.exclusive()

    def exclusive(self):
        self.label(text="Interface: ", row=2, column=0)
        interface = dict()
        self.label(text="Name: ", row=4, column=0, padx=15)
        interface['name'] = self.entry(row=4, column=1)
        self.label(text="MAC address: ", row=5, column=0, padx=15)
        interface['mac_address'] = self.entry(row=5, column=1)
        self.label(text="IP address: ", row=6, column=0, padx=15)
        interface['ip_address'] = self.entry(row=6, column=1)
        self.label(text="IP network: ", row=7, column=0, padx=15)
        interface['ip_network'] = self.entry(row=7, column=1)
        self.label(text="Default gateway: ", row=8, column=0, padx=15)
        interface['default_gateway'] = self.entry(row=8, column=1)

        def add_interface():
            Form.tree_append(
                self['interfaces'],
                interface['name'].get(),
                interface['mac_address'].get(),
                interface['ip_address'].get(),
                interface['ip_network'].get(),
                interface['default_gateway'].get()
            )
        self.button(text="Append", row=11, column=1, sticky="nes", command=add_interface)

        self.button(text="Submit", row=50, column=9, command=self.__trigger)

    def __trigger(self):
        print(self)
        self.trigger(self.get_info())

    def get_info(self):
        result = super().get_info()
        result['type'] = 'router'
        return result
