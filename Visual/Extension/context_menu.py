import tkinter
from functools import partial


class ContextMenu:

    def __init__(self, root, canvas, graph):
        self.root = root
        self.canvas = canvas
        self.graph = graph
        self.first = None
        self.root.bind('<Escape>', self.cancel)

    def load(self, objective):
        category = objective.type
        if hasattr(self, "prepare_" + category):
            getattr(self, "prepare_" + category)(objective)

    def cancel(self, event):
        self.first = None

    def prepare_host(self, host):
        menu = tkinter.Menu(self.canvas, tearoff=0)
        menu.add_command(label='Connect', command=partial(self.__prepare_connecting, host.interface.port))
        menu.add_command(label='Send', command=partial(self.__prepare_sending, host))
        menu.add_command(
            label='Disable' if host.active else 'Enable',
            command=partial(self.__disable if host.active else self.__enable, host))
        self.__finalize(menu)

    def prepare_hub(self, hub, a=True):
        menu = tkinter.Menu(self.canvas, tearoff=0)
        connect_menu = tkinter.Menu(menu, tearoff=0)
        for port in hub.ports:
            connect_menu.add_command(
                label="%s, %s" % (port.name, 'not available' if port.link else 'available'),
                command=partial(self.__prepare_connecting, port)
            )
        menu.add_cascade(label='Connect, as', menu=connect_menu)
        menu.add_command(
            label='Disable' if hub.active else 'Enable',
            command=partial(self.__disable if hub.active else self.__enable, hub))
        if a:
            self.__finalize(menu)
        return menu

    def prepare_switch(self, switch):
        menu = self.prepare_hub(switch, False)
        menu.add_command(
            label='Activate STP' if not switch.attributes.get('stp') else 'Deactivate STP',
            command=partial(self.__activate_stp if not switch.attributes.get('stp') else self.__deactivate_stp, switch)
        )
        self.__finalize(menu)

    def prepare_router(self, router):
        menu = tkinter.Menu(self.canvas, tearoff=0)
        connect_menu = tkinter.Menu(menu, tearoff=0)
        menu.add_cascade(label='Connect, as', menu=connect_menu)
        for interface in router.interfaces:
            connect_menu.add_command(
                label="%s, %s" % (interface.port.name, interface.ip_interface.ip),
                command=partial(self.__prepare_connecting, interface.port)
            )
        menu.add_command(
            label='Disable' if router.active else 'Enable',
            command=partial(self.__disable if router.active else self.__enable, router))
        menu.add_command(
            label='Activate RIP' if not router.attributes.get('rip') else 'Deactivate RIP',
            command=partial(self.__activate_rip if not router.attributes.get('rip') else self.__deactivate_rip, router)
        )
        self.__finalize(menu)

    def __finalize(self, menu):
        try:
            _x = self.root.winfo_pointerx()
            _y = self.root.winfo_pointery()
            menu.tk_popup(_x, _y)
        finally:
            menu.grab_release()

    def __prepare_sending(self, host):
        self.first = {
            'from': host,
            'function': 'sendto_'
        }

    def __prepare_connecting(self, port):
        self.first = {
            'from': port,
            'function': 'connectto_'
        }

    def second_load(self, objective):
        if self.first:
            category = objective.type
            if hasattr(self, self.first['function'] + category):
                getattr(self, self.first['function'] + category)(objective)
            self.first = None

    def sendto_host(self, host):
        if self.first['from'] != host:
            self.first['from'].send(host.interface.ip_interface.ip)

    def sendto_router(self, router):
        menu = tkinter.Menu(self.canvas, tearoff=0)

        def sendto_router_interface(source, _interface):
            source.send(_interface.ip_interface.ip)

        for interface in router.interfaces:
            menu.add_command(label="%s, %s" % (interface.port.name, interface.ip_interface.ip), command=partial(sendto_router_interface, self.first['from'], interface))
        self.__finalize(menu)

    def connectto_host(self, host):
        if host.interface.port != self.first['from']:
            self.graph.add_link(self.first['from'], host.interface.port, 20)

    def connectto_hub(self, hub):
        menu = tkinter.Menu(self.canvas, tearoff=0)

        def connectto_hub_port(source, _port):
            self.graph.add_link(source, _port, 20)

        for port in hub.ports:
            menu.add_command(
                label="%s, %s" % (port.name, 'not available' if port.link else 'available'),
                command=partial(connectto_hub_port, self.first['from'], port)
            )
        self.__finalize(menu)

    def connectto_switch(self, switch):
        self.connectto_hub(switch)

    def connectto_router(self, router):
        menu = tkinter.Menu(self.canvas, tearoff=0)

        def connectto_hub_router(source, _port):
            self.graph.add_link(source, _port, 20)

        for interface in router.interfaces:
            menu.add_command(
                label="%s, %s" % (interface.port.name, interface.ip_interface),
                command=partial(connectto_hub_router, self.first['from'], interface.port)
            )
        self.__finalize(menu)

    def __disable(self, objective):
        objective.disable()

    def __enable(self, objective):
        objective.enable()

    def __activate_stp(self, switch):
        switch.activate_stp()

    def __deactivate_stp(self, switch):
        switch.deactivate_stp()

    def __activate_rip(self, router):
        router.activate_rip()

    def __deactivate_rip(self, router):
        router.deactivate_rip()