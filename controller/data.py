from visual import vgraph, vcanvas
import ipaddress as ipa
# TODO edit data here


class Controller:
    __instance = None
    __graph = None
    __canvas = None
    __inspect = None

    @staticmethod
    def get_instance():
        if not Controller.__instance:
            Controller.__instance = Controller()
            Controller.__instance.first = True
        return Controller.__instance

    def get_graph(self):
        return self.__graph

    def subscribe(self, func, *args):
        self.__canvas.subscribe(func, *args)

    def load(self, instance, canvas, **kwargs):
        # TODO add more type
        self.__canvas = canvas
        vcanvas.Canvas.convert(canvas)
        g = self.__graph = vgraph.Graph()
        """
        g.add_vertex(type='pc', name='pc1', x=0, y=0)
        g.add_vertex(type='pc', name='pc2', x=0, y=-10)
        g.add_vertex(type='pc', name='pc3', x=0, y=10)
        g.add_vertex(type='switch', name='switch', x=10, y=0)
        g.add_edge('switch', 'pc1', width=10)
        g.add_edge('switch', 'pc2', width=10)
        g.add_edge('switch', 'pc3', width=10)
        # g.load()
        g.fit_canvas(canvas)
        canvas.tag_raise('vertex')"""
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

        # pc1 = Host(i1, name='A')
        pc1 = g.add_vertex(i1, type='pc', name='A')
        # pc2 = Host(i2, name='B')
        pc2 = g.add_vertex(i2, type='pc', name='B')
        # pc21 = Host(i21, name='C')
        pc21 = g.add_vertex(i21, type='pc', name='C')
        # pc22 = Host(i22, name='D')
        pc22 = g.add_vertex(i22, type='pc', name='D')

        pc31 = g.add_vertex(i31, type='pc', name='E')

        # switch = Switch(name='switch 0')
        switch = g.add_vertex(type='switch', name='switch 0')
        # switch2 = Switch(name='switch 1')
        switch2 = g.add_vertex(type='switch', name='switch 1')
        # router = Router(i0, i20, name='router', routing_table=routing_table)
        router = g.add_vertex(i0, i20, i30, type='router', routing_table=routing_table, name='router')
        # router2 = g.add_vertex()
        # i0.connect(switch)
        # i1.connect(switch)
        # i2.connect(switch)
        # i20.connect(switch2)
        # i21.connect(switch2)
        # i22.connect(switch2)
        # i30.connect(i31)

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

        # g.load()
        g.display(self.__canvas)
        g.fit_canvas(self.__canvas)

        g.display(canvas)
        return
        if kwargs.get("extension", "graphml") == "graphml":
            self.__graph = vgraph.read(instance)
            vcanvas.Canvas.convert(canvas)
            self.__graph.load()
            self.__graph.fit_canvas(canvas)
            self.__graph.display(canvas)
            return
        raise TypeError

    def create(self, info):
        t = info['type']
        g = self.__graph
        func = object

        def my_create(x, y):
            if t == 'pc':
                pc = g.add_vertex(None, type='pc', name=info.get('name', ''))
                pc['x'], pc['y'] = self.__canvas.invert_position(x, y)
                print(x, y, pc['x'], pc['y'])
                pc.display(self.__canvas)
            self.__canvas.unsubscribe(func, 'button-1', 'location')

        func = my_create
        self.__canvas.subscribe(func, 'button-1', 'location')

    def modify(self, modify_info):
        target = self.__canvas.variable.get('inspect')
        if target:
            target.modify(modify_info)
        else:
            raise ValueError
