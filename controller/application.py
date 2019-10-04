from visual import vgraph, vcanvas
from visual import vnetwork as vn
import ipaddress as ipa
import os


class Controller:
    __instance = None
    __graph = None
    __canvas = None
    __inspect = None
    __cache = dict()

    @staticmethod
    def get_instance():
        if not Controller.__instance:
            Controller.__instance = Controller()
        return Controller.__instance

    def exit(self):
        pass

    def test(self):
        self.__controller.inspect()

    def subscribe_inspection(self, func):
        self.__subscribe(func, 'inspect', 'button-1', 'object')

    def subscribe_coords(self, func):
        self.__subscribe(func, 'coords', 'button-1', 'location-motion')

    def subscribe_property(self, func):
        self.__subscribe(func, 'props', 'button-3', 'object')

    def __subscribe(self, func, name, *args):
        self.__cache[name] = func
        self.__canvas.subscribe(func, *args)

    def create(self, info):
        device_type = info['type']
        g = self.__graph

        def my_create(x, y):
            device = None
            if device_type == 'pc':
                device = g.add_vertex(info['interface'],
                                      type='pc',
                                      name=info.get('name', ''),
                                      arp_table=info.get('interface'))
            if device:
                device['x'], device['y'] = self.__canvas.invert_position(x, y)
                device.display(self.__canvas)
            self.__canvas.unsubscribe(my_create, 'button-1', 'location')

        self.__canvas.subscribe(my_create, 'button-1', 'location')

    def modify_device(self, modify_info):
        warp = self.left_click()
        if warp:
            target = warp.get_variable()
            target.modify(modify_info)

    def add_interface(self, interface_info):
        warp = self.right_click()
        if warp:
            target = warp.get_variable()
            target.add_interface(interface_info)
            warp = self.left_click()
            if warp and warp.get_variable():
                warp.trigger(warp.get_variable().info())

    name = ''
    device_1 = None
    require = False

    def select_interface(self, name):
        self.name = name
        if self.require:
            self.require = False
            self.__connect_with()
        else:
            self.prepare_connecting()

    save = None

    def __isolate(self, interface):
        device = interface.device
        if isinstance(device, vn.PC) or isinstance(device, vn.Router):
            other = interface.other
            if other:
                intersection = device.link_edges.intersection(other.device.link_edges)
                for edge in intersection.copy():
                    if interface in edge.interfaces:
                        edge.destroy(self.__canvas)
                interface.other = None

    def __connect_with(self):

        # What a messy

        if self.device_1 is None:
            self.device_1 = self.right_click().get_variable()
            if isinstance(self.device_1, vn.Router):
                self.device_1 = self.device_1.get_interface(self.name)
            elif isinstance(self.device_1, vn.PC):
                self.device_1 = self.device_1.interface
            self.require = True
        device_2 = self.__canvas.cache[self.__connect_with].get_variable()
        if isinstance(device_2, vgraph.Vertex):
            if isinstance(device_2, vn.Router):
                if self.require:
                    info = self.left_click().get_variable().info()
                    from gui_support import router_connect
                    router_connect(info)
                    return
                device_2 = device_2.get_interface(self.name)
            elif isinstance(device_2, vn.PC):
                device_2 = device_2.interface
            intersection = self.device_1.device.link_edges.intersection(device_2.device.link_edges)
            if len(intersection) > 0:
                pass
                # print(device_1.name, 'and', device_2.name, 'are already connected')
            else:
                self.__isolate(self.device_1)
                self.__isolate(device_2)
                edge = self.__graph.add_edge(self.device_1, device_2)
                self.device_1.connect(device_2)
                edge.display(self.__canvas)
                self.__canvas.tag_lower('edge')
        self.device_1.device.unfocus(self.__canvas)
        self.__canvas.unsubscribe(self.__connect_with, 'button-1', 'empty')
        self.device_1 = None
        self.require = False

    def prepare_connecting(self, *args):
        if self.save:
            self.save.unfocus(self.__canvas)
            self.__canvas.unsubscribe(self.__connect_with, 'button-1', 'empty')
        self.save = self.right_click().get_variable()
        self.save.focus(self.__canvas)
        self.__canvas.subscribe(self.__connect_with, 'button-1', 'empty')

    def send_message(self, *args):
        sender = self.right_click().get_variable()

        def trigger_message():
            receiver = self.left_click().get_variable()
            if sender is not receiver and isinstance(receiver, vn.PC):
                sender.send(self.__canvas, receiver.interface.ip_address)
            self.__canvas.unsubscribe(trigger_message, 'button-1', 'empty')

        self.__canvas.subscribe(trigger_message, 'button-1', 'empty')

    def disable_device(self, *args):
        device = self.right_click().get_variable()
        device.disable(self.__canvas)

    def right_click(self):
        return self.__canvas.cache[self.__cache['props']]

    def left_click(self):
        return self.__canvas.cache[self.__cache['inspect']]

    def load(self, file, canvas):
        # _, extension = os.path.splitext(file.name)
        # self.__controller.load(file, canvas, extension=extension[1:])

        vcanvas.Canvas.convert(canvas)
        self.__canvas = canvas

        # Testing
        g = self.__graph = vgraph.Graph()
        from network import devices as dv
        interface0 = {
            'name': 'interface0',
            'ip_address': ipa.ip_address('192.168.0.1'),
            'ip_network': ipa.ip_network('192.168.0.0/24'),
            'mac_address': 'aa.aa.aa.aa.aa.aa',
        }
        interface1 = {
            'name': 'interface1',
            'ip_address': ipa.ip_address('192.168.0.2'),
            'ip_network': ipa.ip_network('192.168.0.0/24'),
            'mac_address': 'aa.aa.aa.aa.aa.bb',
            'default_gateway': ipa.ip_address('192.168.0.1')
        }
        interface2 = {
            'name': 'interface2',
            'ip_address': ipa.ip_address('192.168.0.3'),
            'ip_network': ipa.ip_network('192.168.0.0/24'),
            'mac_address': 'aa.aa.aa.aa.aa.cc',
            'default_gateway': ipa.ip_address('192.168.0.1')
        }
        interface20 = {
            'name': 'interface20',
            'ip_address': ipa.ip_address('10.10.0.1'),
            'ip_network': ipa.ip_network('10.10.0.0/24'),
            'mac_address': 'aa.aa.aa.aa.aa.00'
        }
        interface21 = {
            'name': 'interface21',
            'ip_address': ipa.ip_address('10.10.0.2'),
            'ip_network': ipa.ip_network('10.10.0.0/24'),
            'mac_address': 'aa.aa.aa.aa.aa.11',
            'default_gateway': ipa.ip_address('10.10.0.1')
        }
        interface22 = {
            'name': 'interface22',
            'ip_address': ipa.ip_address('10.10.0.3'),
            'ip_network': ipa.ip_network('10.10.0.0/24'),
            'mac_address': 'aa.aa.aa.aa.aa.22',
            'default_gateway': ipa.ip_address('10.10.0.1')
        }
        interface30 = {
            'name': 'interface31',
            'ip_address': ipa.ip_address('172.16.0.1'),
            'ip_network': ipa.ip_network('172.16.0.0/20'),
            'mac_address': 'aa.aa.aa.aa.aa.22'
        }
        interface31 = {
            'name': 'interface32',
            'ip_address': ipa.ip_address('172.16.0.2'),
            'ip_network': ipa.ip_network('172.16.0.0/20'),
            'mac_address': 'aa.aa.aa.aa.aa.ff',
            'default_gateway': ipa.ip_address('172.16.0.1')
        }
        i1 = dv.Interface(**interface1)
        i2 = dv.Interface(**interface2)
        i0 = dv.Interface(**interface0)
        i21 = dv.Interface(**interface21)
        i22 = dv.Interface(**interface22)
        i20 = dv.Interface(**interface20)
        i30 = dv.Interface(**interface30)
        i31 = dv.Interface(**interface31)
        routing_table = {
            ipa.ip_network('192.168.0.0/24'): i0,
            ipa.ip_network('10.10.0.0/24'): i20,
            ipa.ip_network('172.16.0.0/20'): i30,
        }
        pc1 = g.add_vertex(i1, type='pc', name='A')
        pc2 = g.add_vertex(i2, type='pc', name='B')
        pc21 = g.add_vertex(i21, type='pc', name='C')
        pc22 = g.add_vertex(i22, type='pc', name='D')
        pc31 = g.add_vertex(i31, type='pc', name='E')
        switch = g.add_vertex(type='switch', name='switch 0')
        switch2 = g.add_vertex(type='switch', name='switch 1')
        router = g.add_vertex(i0, i20, i30, type='router', routing_table=routing_table, name='router')
        g.connect_interface(i1, switch)
        g.connect_interface(i2, switch)
        g.connect_interface(i0, switch)
        g.connect_interface(i20, switch2)
        g.connect_interface(i21, switch2)
        g.connect_interface(i22, switch2)
        g.connect_interface(i31, i30)
        pc1['x'] = -6
        pc1['y'] = -6
        pc2['x'] = -5
        pc2['y'] = 6
        pc31['x'] = 0
        pc31['y'] = 10
        pc21['x'] = 0
        pc21['y'] = -6
        pc22['x'] = 7
        pc22['y'] = 6
        switch['x'] = -5
        switch2['x'] = 5

        g.display(self.__canvas)
        g.fit_canvas(self.__canvas)
