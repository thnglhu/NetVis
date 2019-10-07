from support.device_addition_forms import *


class HostInfo(HostForm):
    def __init__(self, master, info, trigger=None):
        super().__init__(master, trigger)
        Form.entry_set(self['name'], info['name'])
        interface = self['interface']
        interface_info = info['interface']
        Form.entry_set(interface['name'], interface_info['name'])
        Form.entry_set(interface['mac_address'], interface_info['mac_address'])
        Form.entry_set(interface['ip_address'], interface_info['ip_address'])
        Form.entry_set(interface['ip_network'], interface_info['ip_network'])
        Form.entry_set(interface['default_gateway'], interface_info['default_gateway'])
        for ip_address, mac_address in info['arp_table'].items():
            Form.tree_append(self['arp_table'], ip_address, mac_address)

    def exclusive(self):
        self.label(text="ARP table: ", row=7, column=1)
        self['arp_table'] = self.tree_view(
            headers=('IP address', 'MAC address'),
            row=8,
            column=0,
            columnspan=4,
            padx=10,
            sticky="we"
        )
        self.label(text="IP address", row=9, column=1)
        self.label(text="MAC address", row=9, column=2)
        ip_address = self.entry(row=10, column=1)
        mac_address = self.entry(row=10, column=2)

        def append():
            Form.tree_append(self['arp_table'], ip_address.get(), mac_address.get())
            Form.entry_set(ip_address, '')
            Form.entry_set(mac_address, '')

        self.button(text="Append", row=43, column=2, command=append)
        self.button(text="Modify", row=50, column=1, command=self.__trigger)

    def __trigger(self):
        self.trigger(self.get_info())


class SwitchInfo(SwitchForm):
    def __init__(self, master, info, trigger=None):
        super().__init__(master, trigger)
        Form.entry_set(self['name'], info['name'])
        for mac_address, interface in info['mac_table'].items():
            Form.tree_append(self['mac_table'], mac_address, interface)

    def exclusive(self):
        self.label(text="Mac table: ", row=1, column=1)
        self['mac_table'] = self.tree_view(
            headers=("MAC address", "interface"),
            row=2,
            column=0,
            columnspan=4,
            padx=10,
            sticky="we"
        )
        self.button(text="Modify", row=50, column=1, command=self.__trigger)

    def __trigger(self):
        self.trigger(self.get_info())


class RouterInfo(RouterForm):
    def __init__(self, master, info, trigger=None):
        super().__init__(master, trigger)
        Form.entry_set(self['name'], info['name'])
        for interface in info['interfaces']:
            Form.tree_append(
                self['interfaces'],
                interface['name'],
                interface['mac_address'],
                interface['ip_address'],
                interface['ip_network'],
                interface['default_gateway']
            )
        for ip_address, mac_address in info['arp_table'].items():
            Form.tree_append(self['arp_table'], ip_address, mac_address)
        for rule, detail in info['routing_table'].items():
            Form.tree_append(
                self['routing_table'],
                str(rule),
                str(detail['next_hop']),
                str(detail['interface'].ip_address),
                str(detail['type']),
            )

    def exclusive(self):
        self['arp_table'] = self.tree_view(
            headers=('IP address', 'MAC address'),
            row=40,
            column=0,
            columnspan=4,
            padx=10,
            sticky="we"
        )
        self.button(text="Modify", row=50, column=1, command=self.__trigger)

    def __trigger(self):
        self.trigger(self.get_info())