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
        if isinstance(device, vn.Host) or isinstance(device, vn.Router):
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
            elif isinstance(self.device_1, vn.Host):
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
            elif isinstance(device_2, vn.Host):
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
            if sender is not receiver and isinstance(receiver, vn.Host):
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
        vcanvas.Canvas.convert(canvas)
        self.__canvas = canvas
        self.__graph = vgraph.Graph()
        import json
        from network import devices as dv
        with open(file.name) as json_file:
            data = json.load(json_file)
            connectable = dict()
            for device in data['devices']:
                if device['type'] == 'host':
                    interface = connectable[device['interface']['id']] = dv.Interface.load(device['interface'])
                    vertex = self.__graph.add_vertex(interface, type='host', name=device['name'])
                elif device['type'] == 'switch':
                    vertex = self.__graph.add_vertex(type='switch', name=device['name'])
                    connectable[device['id']] = vertex
                elif device['type'] == 'router':
                    interfaces = list()
                    for json in device['interfaces']:
                        interface = dv.Interface.load(json)
                        connectable[json['id']] = interface
                        interfaces.append(interface)
                    vertex = self.__graph.add_vertex(*interfaces, type='router', name=device['name'])
                else:
                    raise KeyError
                vertex['x'] = device['x']
                vertex['y'] = device['y']
            for json in data['connection']:
                self.__graph.connect_interface(
                    connectable[json['link'][0]],
                    connectable[json['link'][1]]
                )
            self.__graph.display(self.__canvas)
            self.__graph.fit_canvas(self.__canvas)

