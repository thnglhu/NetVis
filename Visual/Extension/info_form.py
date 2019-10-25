import tkinter
import tkinter.ttk
import time
from threading import Lock


class InfoForm:

    lock = Lock()

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __init__(self, frame, graph, modify_button, apply_button):
        self.frame = frame
        self.current = None
        self.graph = graph
        self.data = dict()
        self.current_object = None
        self.button = modify_button
        self.apply = apply_button
        self.on = False
        self.apply['state'] = 'disabled'
        self.removed_object = None
        self.remove = False


        modify_button.config(command=self.__trigger)
        apply_button.config(command=self.__modify)

    def __trigger(self):
        self.on = not self.on
        self.button.config(relief=tkinter.SUNKEN if self.on else tkinter.RAISED)
        self.set_modification_mode(self.on)
        self.apply['state'] = 'normal' if self.on and self.current_object else 'disabled'

    def __modify(self):
        if self.on and self.current_object:
            category = self.current_object.type
            if hasattr(self, 'modify_' + category):
                getattr(self, 'modify_' + category)()

    def set_modification_mode(self, unlock):
        if self.current_object:
            category = self.current_object.type
            if hasattr(self, ('unlock_' if unlock else 'lock_') + category):
                getattr(self, ('unlock_' if unlock else 'lock_') + category)()
            if unlock:
                self.current_object.remove_inspector()
            else:
                self.current_object.set_inspector(self.load)
                self.current_object.update()

    def load(self, objective):
        if self.removed_object == objective:
            self.removed_object = None
            self.clear()
            return
        self.removed_object = None
        if self.on:
            self.__trigger()
        if not objective:
            self.clear()
            return

        category = objective.type
        if self.current_object != objective:
            if self.current_object:
                self.current_object.remove_inspector()
            self.current_object = objective
            objective.set_inspector(self.load)
        if category != self.current:
            self.clear()
            self.current = category
            if hasattr(self, "prepare_" + category):
                getattr(self, "prepare_" + category)()
                self.frame.update()
            else:
                return
        getattr(self, "write_" + category)(objective)

    def delete(self, objective):
        if self.remove:
            self.removed_object = objective
            self.graph.remove_device(objective)
            self.remove = False
            self.clear()

    def clear(self):
        for key, child in self.data.copy().items():
            child.destroy()
            self.data.pop(key)
        self.current = None
        # self.current_object = None

    # region Host
    def prepare_host(self):
        self['Name'] = tkinter.Label(self.frame, text="Name: ")
        self['Name'].grid(row=0, column=0, sticky="W")

        self['Name entry'] = tkinter.Entry(self.frame, state='readonly')
        self['Name entry'].grid(row=0, column=1, sticky="W")

        self['DefaultGateway'] = tkinter.Label(self.frame, text="Default gateway: ")
        self['DefaultGateway'].grid(row=1, column=0, sticky="W")

        self['DefaultGateway entry'] = tkinter.Entry(self.frame, state='readonly')
        self['DefaultGateway entry'].grid(row=1, column=1, sticky="W")

        self['Interface'] = tkinter.Label(self.frame, text="Interface: ")
        self['Interface'].grid(row=2, column=0, sticky="W")

        self['PortName'] = tkinter.Label(self.frame, text="Port name: ")
        self['PortName'].grid(row=3, column=0, padx=10, sticky="W")

        self['PortName entry'] = tkinter.Entry(self.frame, state='readonly')
        self['PortName entry'].grid(row=3, column=1, sticky="W")

        self['MacAddress'] = tkinter.Label(self.frame, text="Mac Address: ")
        self['MacAddress'].grid(row=4, column=0, padx=10, sticky="W")

        self['MacAddress entry'] = tkinter.Entry(self.frame, state='readonly')
        self['MacAddress entry'].grid(row=4, column=1, sticky="W")

        self['IpInterface'] = tkinter.Label(self.frame, text="IP Interface: ")
        self['IpInterface'].grid(row=5, column=0, padx=10, sticky="W")

        self['IpInterface entry'] = tkinter.Entry(self.frame, state='readonly')
        self['IpInterface entry'].grid(row=5, column=1, sticky="W")

        self['ARPTable'] = tkinter.Label(self.frame, text="ARP Table")
        self['ARPTable'].grid(row=6, column=0, sticky="W")

        self['ARPTable treeview'] = self.tree_view(self.frame, ['IP address', 'MAC address', 'Last Time'])
        self['ARPTable treeview'].grid(row=7, column=0, padx=10, sticky="WE", columnspan=2)

    def write_host(self, host):
        self.set_entry_text(self['Name entry'], host.name)
        self.set_entry_text(self['DefaultGateway entry'], host.default_gateway)
        self.set_entry_text(self['PortName entry'], host.interface.port.name)
        self.set_entry_text(self['MacAddress entry'], host.interface.mac_address)
        self.set_entry_text(self['IpInterface entry'], str(host.interface.ip_interface))
        self.set_treeview(self['ARPTable treeview'], [
            [key, value['mac_address'], time.strftime('%H:%M:%S', time.localtime(value['time']))] for key, value in host.interface.arp_table.items()
        ])

    def unlock_host(self, state='normal'):
        self['Name entry']['state'] = state
        self['DefaultGateway entry']['state'] = state
        self['PortName entry']['state'] = state
        self['MacAddress entry']['state'] = state
        self['IpInterface entry']['state'] = state

    def lock_host(self):
        self.unlock_host('readonly')

    def modify_host(self):
        self.current_object.modify({
            'name': self['Name entry'].get(),
            'default_gateway': self['DefaultGateway entry'].get(),
            'interface': {
                'mac_address': self['MacAddress entry'].get(),
                'ip_interface': self['IpInterface entry'].get(),
                'port': {
                    'name': self['PortName entry'].get(),
                }
            }
        })
        self.__trigger()
    # endregion

    # region Hub
    def prepare_hub(self):
        self['Name'] = tkinter.Label(self.frame, text="Name: ")
        self['Name'].grid(row=0, column=0, sticky="W")

        self['Name entry'] = tkinter.Entry(self.frame, state='readonly')
        self['Name entry'].grid(row=0, column=1, sticky="W")

        self['Ports'] = tkinter.Label(self.frame, text="Ports: ")
        self['Ports'].grid(row=12, column=0, padx=10, sticky="W")

        self['Port treeview'] = self.tree_view(self.frame, ['Name', 'Availability'])
        self['Port treeview'].grid(row=13, column=0, padx=10, sticky="WE", columnspan=2)

    def write_hub(self, hub):
        self.set_entry_text(self['Name entry'], hub.name)
        self.set_treeview(self['Port treeview'], [
            [port.name, not bool(port.link)] for port in hub.ports
        ])

    def unlock_hub(self, state='normal'):
        self['Name entry']['state'] = state

    def lock_hub(self):
        self.unlock_hub('readonly')

    def modify_hub(self):
        self.current_object.modify({
            'name': self['Name entry'].get(),
        })
        self.__trigger()

    # endregion

    # region Switch
    def prepare_switch(self):
        self.prepare_hub()

        self['Port treeview'].grid_forget()
        self['Port treeview'] = self.tree_view(self.frame, ['Name', 'MAC Address', 'Availability', 'State'])
        self['Port treeview'].grid(row=13, column=0, padx=10, sticky="WE", columnspan=4)

        self['MACTable'] = tkinter.Label(self.frame, text="MAC Table: ")
        self['MACTable'].grid(row=24, column=0, padx=10, sticky="W")

        self['MACTable treeview'] = self.tree_view(self.frame, ['MAC address', 'Port', 'Last Time'])
        self['MACTable treeview'].grid(row=25, column=0, padx=10, sticky="WE", columnspan=4)

    def write_switch(self, switch):
        self.set_entry_text(self['Name entry'], switch.name)
        self.set_treeview(self['Port treeview'], [
            [port.name, port.mac_address, not bool(port.link), 'designated' if not switch.attributes.get('stp') else switch.ports[port]['state']] for port in switch.ports
        ])
        self.set_treeview(self['MACTable treeview'], [
            [key, value['port'].name, time.strftime('%H:%M:%S', time.localtime(value['time']))] for key, value in switch.mac_table.items()
        ])

    def unlock_switch(self, state='normal'):
        self['Name entry']['state'] = state

    def lock_switch(self):
        self.unlock_switch('readonly')

    def modify_switch(self):
        self.current_object.modify({
            'name': self['Name entry'].get(),
        })
        self.__trigger()
    # endregion

    # region Router
    def prepare_router(self):
        self['Name'] = tkinter.Label(self.frame, text="Name: ")
        self['Name'].grid(row=0, column=0, sticky="W")

        self['Name entry'] = tkinter.Entry(self.frame, state='readonly')
        self['Name entry'].grid(row=0, column=1, sticky="W")

        self['Interfaces'] = tkinter.Label(self.frame, text="Interfaces: ")
        self['Interfaces'].grid(row=1, column=0, sticky="W")

        self['Interface treeview'] = self.tree_view(self.frame, ['Interface', 'IP Interface',  'MAC Address'])
        self['Interface treeview'].grid(row=2, column=0, padx=10, sticky="WE", columnspan=4)

        self['ARPTable'] = tkinter.Label(self.frame, text="ARP Table: ")
        self['ARPTable'].grid(row=13, column=0, sticky="W")

        self['ARPTable treeview'] = self.tree_view(self.frame, ['Interface', 'IP Interface',  'MAC Address', 'Last Time'])
        self['ARPTable treeview'].grid(row=14, column=0, padx=10, sticky="WE", columnspan=4)

        self['StaticRoutingTable'] = tkinter.Label(self.frame, text="Static Routing Table:")
        self['StaticRoutingTable'].grid(row=25, column=0, sticky="W")

        self['StaticRoutingTable treeview'] = self.tree_view(self.frame, ['Network', 'Next hop', 'Interface'])
        self['StaticRoutingTable treeview'].grid(row=26, column=0, padx=10, sticky="WE", columnspan=4)

        self['RIP'] = tkinter.Label(self.frame, text="RIP Table:")
        self['RIP'].grid(row=35, column=0, sticky="W")

        self['RIP treeview'] = self.tree_view(self.frame, ['Network', 'Hop', 'Via', 'Interface'])
        self['RIP treeview'].grid(row=36, column=0, padx=10, sticky="WE", columnspan=4)

    def write_router(self, router):
        self.set_entry_text(self['Name entry'], router.name)
        self.set_treeview(self['Interface treeview'], [
            [interface.port.name, interface.mac_address, str(interface.ip_interface)] for interface in router.interfaces
        ])
        self.set_treeview(self['ARPTable treeview'], [
            [interface.port.name, key, value['mac_address'], time.strftime('%H:%M:%S', time.localtime(value['time']))]
            for interface in router.interfaces for key, value in interface.arp_table.items()
        ])
        self.set_treeview(self['StaticRoutingTable treeview'], [
            [str(rule['network']), rule['next_hop'] if rule['next_hop'] else '-', rule['interface'].port.name] for rule in router.routing_table
        ])
        self.set_treeview(self['RIP treeview'], [] if not router.attributes.get('rip') else [
            [network, info['hop'], info['via'], info['interface'].port.name]
            for network, info in router['rip']['table'].items()
        ])

    def unlock_router(self, state='normal'):
        self['Name entry']['state'] = state

    def lock_router(self):
        self.unlock_router('readonly')

    def modify_router(self):
        self.current_object.modify({
            'name': self['Name entry'].get(),
        })
        self.__trigger()

    def prepare_link(self):
        self['Bandwidth'] = tkinter.Label(self.frame, text='Bandwidth: ')
        self['Bandwidth'].grid(row=0, column=0, sticky="W")

        self['Bandwidth entry'] = tkinter.Entry(self.frame, state='readonly')
        self['Bandwidth entry'].grid(row=0, column=1, sticky="W")

    def write_link(self, link):
        InfoForm.set_entry_text(self['Bandwidth entry'], link.bandwidth)

    def unlock_link(self, state='normal'):
        self['Bandwidth entry']['state'] = state

    def lock_link(self):
        self.unlock_link('readonly')

    def modify_link(self):
        self.current_object.modify({
            'bandwidth': self['Bandwidth entry'].get(),
        })
        self.__trigger()
    # endregion

    # region Support
    @staticmethod
    def set_entry_text(entry, text):
        readonly = False
        if entry['state'] == 'readonly':
            readonly = True
            entry['state'] = 'normal'
        entry.delete(0, tkinter.END)
        entry.insert(0, text)
        if readonly:
            entry['state'] = 'readonly'

    @staticmethod
    def tree_view(root, headers, deletable=False):
        tree = tkinter.ttk.Treeview(root, columns=[str(i + 1) for i in range(len(headers) - 1)])
        tree.heading('#0', text=headers[0])
        tree.column('#0', minwidth=20, width=100)
        for i in range(len(headers) - 1):
            tree.heading(str(i + 1), text=headers[i + 1])
            tree.column(str(i + 1), minwidth=20, width=100)
        if deletable:
            def delete(_):
                for item in tree.selection():
                    tree.delete(item)

            tree.bind("<Delete>", delete)
        return tree

    @classmethod
    def set_treeview(cls, treeview, data):
        cls.lock.acquire()
        for child in treeview.get_children():
            try:
                treeview.delete(child)
            except:
                pass
        cls.lock.release()
        for datum in data:
            InfoForm.insert_treeview(treeview, datum)

    @staticmethod
    def insert_treeview(treeview, datum):
        treeview.insert('', tkinter.END, text=datum[0], values=datum[1:])

    @staticmethod
    def get_treeview(treeview):
        result = list()
        for child in treeview.get_children():
            result.append([treeview.item(child)['text']] + treeview.item(child)['values'])
        return result
    # endregion
