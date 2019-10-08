from visual import vgraph, vcanvas
from visual import vnetwork as vn
import ipaddress as ipa
import os
import json


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

    def init(self, canvas):
        vcanvas.Canvas.convert(canvas)
        self.__canvas = canvas
        self.__graph = vgraph.Graph()

    def load_file(self, file):
        self.clear()
        with open(file.name) as json_file:
            data = json.load(json_file)
            time_stamp = data['time_stamp']
            connectable = dict()
            switches = dict()
            routers = dict()
            for device in data['devices']:
                from network import devices as dv
                if device['type'] == 'host':
                    interface = connectable[device['interface']['id']] = dv.Interface.load(device['interface'])
                    vertex = self.__graph.add_vertex(interface, type='host', name=device['name'], arp_table=device['arp_table'])
                    vertex.fix_time_stamp(time_stamp)
                elif device['type'] == 'switch':
                    vertex = self.__graph.add_vertex(device['mac_address'], type='switch', name=device['name'])
                    connectable[device['id']] = vertex
                    switches[vertex] = device
                elif device['type'] == 'router':
                    interfaces = list()
                    for json_info in device['interfaces']:
                        interface = dv.Interface.load(json_info)
                        connectable[json_info['id']] = interface
                        interfaces.append(interface)
                    vertex = self.__graph.add_vertex(*interfaces, type='router', name=device['name'])
                    routers[vertex] = device
                else:
                    raise KeyError
                vertex['x'] = device['x']
                vertex['y'] = device['y']
            for switch, device in switches.items():
                switch.set_mac_table({
                    key: connectable[value] for key, value in device['mac_table'].items()
                })
                switch.activate_stp(self.__canvas)
            for router, device in routers.items():
                router.set_routing_table(device['routing_table'])

            for json_info in data['connection']:
                edge = self.__graph.connect_interface(
                    connectable[json_info['link'][0]],
                    connectable[json_info['link'][1]]
                )
                edge['bandwidth'] = json_info['bandwidth']
            self.__graph.display(self.__canvas)
            self.__graph.fit_canvas(self.__canvas)

    def save_file(self, file):
        with open(file.name, 'w') as json_file:
            json.dump(self.__graph.json(), json_file, sort_keys=True, indent=4)

    def exit(self):
        pass

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
            from network import devices as dv
            device = None
            if device_type == 'host':
                interface = dv.Interface.load(info['interface'])
                device = self.__graph.add_vertex(
                    interface,
                    type='host',
                    name=info['name'],
                )
            elif device_type == 'switch':
                device = self.__graph.add_vertex(
                    info['mac_address'],
                    type='switch',
                    name=info['name']
                )
            elif device_type == 'router':
                interfaces = list(map(lambda interface_info: dv.Interface.load(interface_info), info['interfaces']))
                device = self.__graph.add_vertex(
                    *interfaces,
                    type='router',
                    name=info['name']
                )
                device.set_routing_table(info.get('routing_table'))
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

    __save = None

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
        return

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
                edge['bandwidth'] = 50
                edge.display(self.__canvas)
                self.__canvas.tag_lower('edge')
        self.device_1.device.unfocus(self.__canvas)
        self.__canvas.unsubscribe(self.__connect_with, 'button-1', 'empty')
        self.device_1 = None
        self.require = False

    def prepare_connecting(self, *args):
        if self.__save:
            self.__save.unfocus(self.__canvas)
            self.__canvas.unsubscribe(self.__connect_with, 'button-1', 'empty')
        self.__save = self.right_click().get_variable()
        self.__save.focus(self.__canvas)
        self.__canvas.subscribe(self.__connect_with, 'button-1', 'empty')

    def send_message(self, *args):
        sender = self.right_click().get_variable()

        def trigger_message():
            receiver = self.left_click().get_variable()
            if sender is not receiver and isinstance(receiver, vn.Host):
                sender.send(self.__canvas, receiver.interface.ip_address)
            self.__canvas.unsubscribe(trigger_message, 'button-1', 'empty')

        self.__canvas.subscribe(trigger_message, 'button-1', 'empty')

    def activate_stp(self, *args):
        device = self.right_click().get_variable()
        if device['type'] == 'switch':
            device.activate_stp(self.__canvas)

    def disable_device(self, *args):
        device = self.right_click().get_variable()
        device.disable(self.__canvas)

    def clear(self):
        self.__canvas.clear()
        self.__graph = vgraph.Graph()

    def right_click(self):
        return self.__canvas.cache[self.__cache['props']]

    def left_click(self):
        return self.__canvas.cache[self.__cache['inspect']]



