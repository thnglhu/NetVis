from abc import ABC, abstractmethod
from collections.abc import Iterable
# Abstract base class (ABC)

import igraph as ig
import numpy as np
from scipy.spatial import ConvexHull


def read(filename, *args, **kwargs):
    graph = ig.read(filename, *args, **kwargs)
    Graph.convert(graph)
    return graph


class Graph(ig.Graph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__init_subclass()

    def __init_subclass(self):

        def shorten(element, attributes, *key_default):
            for key, value in key_default:
                element[key] = attributes.get(key, value) or value

        for i, v in enumerate(self.vs):
            va = v.attributes()
            keys = ['x', 'y', 'size', 'width', 'color', 'tag', 'index', 'state', 'focus_color']
            defaults = [0, 0, 10, 2, 'red', {'vertex'}, i, 'normal', 'pink']
            shorten(v, va, *zip(keys, defaults))
        self.vertices = list(map(lambda v: Vertex(v), self.vs))

        for i, e in enumerate(self.es):
            ea = e.attributes()
            keys = ['width', 'color', 'tag', 'focus_color']
            defaults = [2, 'black', {'edge'}, 'gray']
            shorten(e, ea, *zip(keys, defaults))
        self.edges = list(map(lambda e: Edge(e, self), self.es))
        # self.hulls = []
        self.__backup = self.copy()
        self.load()
        # self.threads = [None] * 10

    def display(self, canvas):
        for e in self.edges:
            e.display(canvas)
        for v in self.vertices:
            v.display(canvas)
        # for hull in self.hulls: hull.display(canvas)
        canvas.fix_order()

    def fit_canvas(self, canvas):
        vertices = [[], []]
        try:
            vertices[0] = self.vs['x']
        except AttributeError:
            vertices[0] = [0] * len(self.vs)
        try:
            vertices[1] = self.vs['y']
        except AttributeError:
            vertices[1] = [0] * len(self.vs)
        top_left = min(vertices[0]), min(vertices[1])
        bottom_right = max(vertices[0]), max(vertices[1])
        canvas.scale_to_fit(top_left, bottom_right)

    def load(self):
        for v in self.vertices:
            v.load();
        for e in self.edges:
            e.load()
        # for h in self.hulls: h.load()

    def convex_hull(self, indices):
        vertices = list(map(lambda index: self.vertices[index], indices))
        # self.hulls = [Hull(vertices)]

    def add_vertices(self, n):
        super().add_vertices(n)


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
    def __init__(self, *items):
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


class CanvasItem(ABC):
    def __init__(self):
        self.attributes = dict()

    def __getitem__(self, key):
        return self.attributes[key]

    @abstractmethod
    def load(self): pass

    def display(self, canvas): pass

    def focus(self, canvas): pass

    def blur(self, canvas): pass

    def motion(self, canvas, delta_x, delta_y): pass


class Vertex(CanvasItem):
    def __init__(self, ig_vertex):
        super().__init__()
        self.ig_vertex = ig_vertex
        self.link_edges = set()

    def load(self):
        for key in self.ig_vertex.attribute_names():
            self.attributes[key] = self.ig_vertex[key]

    def display(self, canvas):
        att = self.attributes
        canvas.create_mapped_circle(self, att['x'], att['y'], att['size'], width=att['width']+0.5, fill=att['color'],
                                    tag=list(att['tag']), activewidth=att['width'] + 2.5)

    def visual(self):
        pass
        # print("Vectex: ", self.x, self.y, self.size, self.color, self.width)

    def focus(self, canvas):
        att = self.attributes
        att['color'] = att['focus_color']
        att['tag'].add('highlight')
        self.display(canvas)
        canvas.center_to((att['x'], att['y']))

    def blur(self, canvas):
        att = self.attributes
        att['color'] = self.ig_vertex['color']
        att['focus_size'] = self.ig_vertex['size']
        att['tag'].remove('highlight')
        self.display(canvas)

    def graph(self):
        return self.ig_vertex.graph

    def motion(self, canvas, delta_x, delta_y):
        self.attributes['x'] += delta_x
        self.attributes['y'] += delta_y
        self.display(canvas)
        for edge in self.link_edges: edge.display(canvas)

    def subscribe(self, edge):
        self.link_edges.add(edge)


class Edge(CanvasItem):
    def __init__(self, ig_edge, graph):
        super().__init__()
        self.ig_edge = ig_edge
        self.points = tuple(map(lambda v: graph.vertices[v], ig_edge.tuple))
        self.points[0].subscribe(self)
        self.points[1].subscribe(self)

    def load(self):
        for key in self.ig_edge.attribute_names():
            self.attributes[key] = self.ig_edge[key]

    def packed_points(self):
        def shorten(idx, axis):
            return self.points[idx].attributes[axis]
        return shorten(0, 'x'), shorten(0, 'y'), shorten(1, 'x'), shorten(1, 'y')

    def display(self, canvas):
        att = self.attributes
        canvas.create_mapped_line(self, *self.packed_points(), width=att['width'], fill=att['color'], tag=list(att['tag']), activewidth=att['width'] + 1)

    def visual(self):
        att = self.attributes
        print("Edge: ", *self.packed_points(), att['color'], att['width'])

    def focus(self, canvas):
        att = self.attributes
        att['color'] = self.ig_edge['focus_color']
        att['tag'].add('highlight')
        self.display(canvas)
        a, b, x, y = self.packed_points()
        canvas.scale_to_fit((a, b), (x, y))
        # canvas.center_to(((a + x) / 2, (b + y) / 2))

    def blur(self, canvas):
        att = self.attributes
        att['tag'].remove('highlight')
        att['color'] = self.ig_edge['color']
        self.display(canvas)

    def graph(self):
        return self.ig_edge.graph


class Hull:
    def __init__(self, *vertices, **kwargs):
        self.vertices = vertices
        self.points = None

    def display(self, canvas):
        canvas.create_polygon(*self.points, fill='green')

    def load(self):
        points = np.array(list(map(lambda vertex: (vertex.attributes['x'], vertex.attributes['y']), self.vertices)))
        convex_hull = ConvexHull(points)
        print(points)
        self.points = list(map(lambda index: points[index], convex_hull.vertices))
