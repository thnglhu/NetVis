from abc import ABC, abstractmethod
from collections.abc import Iterable
# Abstract base class (ABC)

import igraph as ig
import numpy as np
import operator
import time
from scipy.spatial import ConvexHull


def read(filename, *args, **kwargs):
    graph = ig.read(filename, *args, **kwargs)
    Graph.convert(graph)
    return graph


class Graph(ig.Graph):
    __defaults = dict()
    __defaults['vertex'] = (
        ('x', 0),
        ('y', 0),
        ('type', 'pc'),
        ('state', 'active'),
        ('tag', {'vertex'})
    )
    __defaults['edge'] = (
        ('width', 2),
        ('color', 'black'),
        ('state', 'active'),
        ('tag', {'edge'})
    )
    connectable = dict()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__init_subclass()

    def __init_subclass(self):
        from . import vnetwork as vn
        self.vertices = list()
        self.edges = list()
        # for vertex in self.vs:
        #     self.__set_default_values(vertex, self.__defaults['vertex'])
        #     self.vertices.append(vn.classification[vertex['type']](vertex))
        # for edge in self.es:
        #     self.__set_default_values(edge, self.__defaults['edge'])
        #     self.vertices.append(Edge(edge, self))
        self.__backup = self.copy()
        self.load()

    @staticmethod
    def __set_default_values(item, defaults):
        for key, value in defaults:
            item[key] = item.attributes().get(key, value) or value

    def display(self, canvas):
        for e in self.edges:
            e.display(canvas)
        for v in self.vertices:
            v.display(canvas)
        canvas.fix_order()

    def fit_canvas(self, canvas):
        x = sorted(self.get_vs()['x'])
        y = sorted(self.get_vs()['y'])
        top_left = x[0], y[0]
        bottom_right = x[-1], y[-1]
        canvas.scale_to_fit(top_left, bottom_right, (50, 50))

    def load(self):
        for v in self.vertices:
            v.load()
        for e in self.edges:
            e.load()
        # for h in self.hulls: h.load()

    def add_vertices(self, n):
        # TODO add vertices
        return super().add_vertices(n)

    def add_vertex(self, *args, **kwargs):
        from . import vnetwork as vn
        super().add_vertex(**kwargs)
        vertex = self.vs[self.vcount() - 1]
        self.__set_default_values(vertex, self.__defaults['vertex'])
        self.vertices.append(vn.classification[vertex['type']](vertex, *args, **kwargs))
        vertex = self.vertices[-1]
        vertex.load()
        return vertex

    def add_edge(self, source, target, *args, **kwargs):
        super().add_edge(source.device.ig_vertex, target.device.ig_vertex, **kwargs)
        edge = self.es[self.ecount() - 1]
        self.__set_default_values(edge, self.__defaults['edge'])
        self.edges.append(Edge(edge, source, target))
        self.edges[-1].load()
        return self.edges[-1]

    def connect_interface(self, interface, device):
        edge = self.add_edge(interface, device)
        interface.connect(device)
        return edge

    def delete_edges(self, *args, **kwds):
        return super().delete_edges(*args, **kwds)

    def get_vs(self, **kwargs):
        seq = ItemSequence(self.vertices, *self.vertices)
        return seq.select(**kwargs)

    def json(self):
        return {
            "devices": [device.json() for device in self.vertices],
            "connection": [link.json() for link in self.edges],
            "time_stamp": time.time(),
        }

    @staticmethod
    def convert(igraph):
        igraph.__class__ = Graph
        igraph.__init_subclass()
        return igraph

    @classmethod
    def Full(cls, n, directed=False, loops=False):
        igraph = ig.Graph.Full(n, directed, loops)
        Graph.convert(igraph)
        return igraph


class ItemSequence:
    def __init__(self, pool, *items):
        self.pool = pool
        self.items = items

    def __setitem__(self, key, value):
        import itertools as it
        values = it.cycle(value) if isinstance(value, Iterable) else it.repeat(value, len(self.items))
        for item in self.items:
            item[key] = next(values)

    def __getitem__(self, key):
        result = list()
        for item in self.items:
            result.append(item[key])
        return result

    def select_from_indices(self, indices):
        items = []
        for index in indices:
            items.append(self.pool[index])
        return ItemSequence(self.pool, *items)

    def select(self, **kwargs):
        result = self
        operators = {
            "lt": operator.lt,
            "gt": operator.gt,
            "le": operator.le,
            "ge": operator.ge,
            "eq": operator.eq,
            "ne": operator.ne,
            "in": lambda a, b: a in b,
            "notin": lambda a, b: a not in b}
        for key, value in kwargs.items():
            if "_" not in key or key.rindex("_") == 0:
                key += "_eq"
            att, _, op = key.rpartition("_")
            try:
                func = operators[op]
            except KeyError:
                att, func = key, operators["eq"]
            if att[0] == "_":
                pass
                raise NotImplementedError
                # values = getattr(self.graph, att[1:])(self)
            else:
                values = result[att]
            indices = [i for i, v in enumerate(values) if func(v, value)]
            result = result.select_from_indices(indices)
        return result


class CanvasItem(ABC):
    active = True

    def __init__(self):
        self.attributes = dict()

    def __getitem__(self, key):
        return self.attributes[key]

    def __setitem__(self, key, value):
        self.attributes[key] = value

    @abstractmethod
    def load(self): pass

    @abstractmethod
    def display(self, canvas): pass

    @abstractmethod
    def reallocate(self, canvas): pass

    @abstractmethod
    def reconfigure(self, canvas): pass

    @abstractmethod
    def focus(self, canvas): pass

    @abstractmethod
    def unfocus(self, canvas): pass

    @abstractmethod
    def info(self): pass

    @abstractmethod
    def destroy(self, canvas): pass

    # @abstractmethod
    def disable(self, canvas):
        self.active = False

    def enable(self, canvas):
        self.active = True

    def motion(self, canvas, delta_x, delta_y): pass


class Vertex(CanvasItem, ABC):
    __focus_circle = None

    def __init__(self, ig_vertex):
        super().__init__()
        self.ig_vertex = ig_vertex
        self.link_edges = set()

    def load(self):
        for key in self.ig_vertex.attribute_names():
            self.attributes[key] = self.ig_vertex[key]

    def visual(self):
        pass
        # print("Vectex: ", self.x, self.y, self.size, self.color, self.width)

    def graph(self):
        return self.ig_vertex.graph

    def motion(self, canvas, delta_x, delta_y):
        self['x'] += delta_x
        self['y'] += delta_y
        self.reallocate(canvas)
        for edge in self.link_edges:
            edge.reallocate(canvas)
        if self.__focus_circle:
            self.__focus_circle.reallocate(canvas)

    def subscribe(self, edge):
        self.link_edges.add(edge)

    def unsubscribe(self, edge):
        if edge in self.link_edges:
            self.link_edges.remove(edge)

    def reallocate(self, canvas):
        att = self.attributes
        canvas.coords_mapped(self, att['x'], att['y'])

    def focus(self, canvas):
        pass

    def unfocus(self, canvas):
        pass

    def destroy(self, canvas):
        pass

class Edge(CanvasItem):

    def __init__(self, ig_edge, interface_1, interface_2):
        super().__init__()
        self.ig_edge = ig_edge
        self.interfaces = (interface_1, interface_2)
        self.points = (interface_1.device, interface_2.device)
        interface_1.device.subscribe(self)
        interface_2.device.subscribe(self)

    # def __init__(self, ig_edge, graph):
    #     super().__init__()
    #     self.ig_edge = ig_edge
    #     self.points = tuple(map(lambda v: graph.vertices[v], ig_edge.tuple))
    #     self.points[0].subscribe(self)
    #     self.points[1].subscribe(self)

    def load(self):
        for key in self.ig_edge.attribute_names():
            self.attributes[key] = self.ig_edge[key]

    def packed_points(self):
        def shorten(idx, axis):
            return self.points[idx].attributes[axis]
        return shorten(0, 'x'), shorten(0, 'y'), shorten(1, 'x'), shorten(1, 'y')


    def display(self, canvas):
        att = self.attributes
        canvas.create_mapped_line(self,
                                  *self.packed_points(),
                                  width=att['width'],
                                  fill=att['color'],
                                  tag=tuple(att['tag']),
                                  activewidth=att['width'] + 1,
                                  dash=(10, 5) if not self.active else None,
                                  )

    def reallocate(self, canvas):
        canvas.coords_mapped(self, *self.packed_points())

    def reconfigure(self, canvas):
        att = self.attributes
        canvas.itemconfig_mapped(self,
                                 width=att['width'],
                                 fill=att['color'],
                                 tag=tuple(att['tag']),
                                 activewidth=att['width'] + 1,
                                 dash=(10, 5) if not self.active else None,
                                 )

    def visual(self):
        att = self.attributes

    def focus(self, canvas):
        pass

    def unfocus(self, canvas):
        pass

    def graph(self):
        return self.ig_edge.graph

    def destroy(self, canvas):
        graph = self.graph()
        a = self.points[0]
        b = self.points[1]
        graph.delete_edges([(a.ig_vertex, b.ig_vertex)])
        graph.edges.remove(self)
        a.unsubscribe(self)
        b.unsubscribe(self)
        canvas.remove(self)

    def disable(self, canvas):
        self.active = False
        self.reconfigure(canvas)

    def info(self):
        return {
            'type': (False, 'edge'),
            'bandwidth': (True, str(self['bandwidth']) + 'bps'),
        }

    def json(self):
        return {
            'link': list(map(
                lambda interface: id(interface),
                self.interfaces
            )),
            'bandwidth': self['bandwidth'],
        }