from support.device_addition_forms import *


class HostInfo(HostForm):
    def __init__(self, master, info, trigger=None):
        super().__init__(master, trigger)
        self.trigger = trigger
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

        self.button(text="Append", row=43, column=2, sticky="nes", command=append)
        self.button(text="Modify", row=43, column=1, sticky="nes", command=self.__trigger)


    def __trigger(self):
        self.trigger(self.get_info())


class SwitchInfo(SwitchForm):
    def __init__(self, master, info, trigger=None):
        super().__init__(master, trigger)
        self.trigger = trigger
        Form.entry_set(self['name'], info['name'])
        Form.entry_set(self['mac_address'], info['mac_address'])
        for mac_address, interface in info['mac_table'].items():
            Form.tree_append(self['mac_table'], mac_address, interface)

        if info.get('STP'):
            self.label(text='STP:', row=0, column=15)
            self.label(text='id: ', row=1, column=15)
            self.label(text=str(info['STP']['id']), row=1, column=16)
            self.label(text='root_id: ', row=2, column=15)
            self.label(text=str(info['STP']['root_id']), row=2, column=16)
            self.label(text='cost: ', row=3, column=15)
            self.label(text=str(info['STP']['cost']), row=3, column=16)

    def exclusive(self):
        self.label(text="Mac table: ", row=5, column=1)
        self['mac_table'] = self.tree_view(
            headers=("MAC address", "interface"),
            row=6,
            column=0,
            columnspan=4,
            padx=10,
            width=75,
            sticky="we"
        )
        self.button(text="Modify", row=70, column=5, sticky="nes", command=self.__trigger)

    def __trigger(self):
        self.trigger(self.get_info())


class RouterInfo(RouterForm):
    def __init__(self, master, info, trigger=None):
        super().__init__(master, trigger)
        self.trigger = trigger
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
        for row in info['arp_table']:
            Form.tree_append(self['arp_table'], row['ip_address'], row['mac_address'])
        for rule, detail in info['routing_table'].items():
            Form.tree_append(
                self['routing_table'],
                str(rule),
                str(detail['next_hop']),
                str(detail['interface'].ip_address),
                str(detail['type']),
            )
        if info.get('RIP_routing_table'):
            self.label(text='RIP table:', row=0, column=15)
            self['RIP_routing_table'] = self.tree_view(
                headers=('IP Network', 'Via', 'Hop'),
                row=1,
                column=15,
                columnspan=4,
                rowspan=6,
                sticky="we",
                padx=10
            )
            for rule in info['RIP_routing_table']:
                Form.tree_append(
                    self['RIP_routing_table'],
                    str(rule['ip_network']),
                    str(rule['via']),
                    str(rule['hop']),
                )

    def exclusive(self):
        self.label(text='ARP table:', row=4, column=0)
        self['arp_table'] = self.tree_view(
            headers=('IP address', 'MAC address'),
            row=5,
            column=0,
            columnspan=4,
            rowspan=6,
            sticky="we",
            padx=10
        )

        self.button(text="Modify", row=11, column=7, sticky="es", command=self.__trigger)

    def __trigger(self):
        self.trigger(self.get_info())