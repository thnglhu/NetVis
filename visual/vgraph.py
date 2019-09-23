import igraph as ig
import numpy as np
from scipy.spatial import ConvexHull

def read(filename, *args, **kwargs):
    igraph = ig.read(filename, *args, **kwargs)
    Graph.convert(igraph)
    return igraph

class Graph(ig.Graph):
    def __init__(self, *args, **kwargs):
        ig.Graph.__init__(self, *args, **kwargs)
        self._init_subclass()
    def _init_subclass(self):
        def shorten(element, attributes, *key_default):
            for pair in key_default:
                element[pair[0]] = attributes.get(pair[0], pair[1]) or pair[1]
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
        self.load()
        #self.threads = [None] * 10

    def display(self, canvas):
        for e in self.edges:
            e.display(canvas)
        for v in self.vertices:
            v.display(canvas)
        # for hull in self.hulls: hull.display(canvas)
        canvas.fix_order()

        #def display_vertices(i, n):
        #    for v in self.vertices[i::n]: v.display(canvas)
        #for i, thread in enumerate(self.threads):
        #    if thread is not None: thread.join()
        #    thread = th.Thread(target=display_vertices, args=(i, len(self.threads)))
        #    thread.start()

    def fit_canvas(self, canvas):
        vertices = [[], []]
        try:
            vertices[0] = self.vs['x']
        except:
            vertices[0] = [0] * len(self.vs)
        try:
            vertices[1] = self.vs['y']
        except:
            vertices[1] = [0] * len(self.vs)
        top_left = min(vertices[0]), min(vertices[1])
        bottom_right = max(vertices[0]), max(vertices[1])
        canvas.scale_to_fit(top_left, bottom_right)

    def load(self):
        for v in self.vertices: v.load();
        for e in self.edges: e.load()
        # for h in self.hulls: h.load()
    def convex_hull(self, indices):
        vertices = list(map(lambda index: self.vertices[index], indices))
        # self.hulls = [Hull(vertices)]

    @classmethod
    def convert(cls, igraph):
        igraph.__class__ = Graph
        igraph._init_subclass()
        return igraph

    @classmethod
    def Full(cls, n, directed=False, loops=False):
        igraph = ig.Graph.Full(n, directed, loops)
        Graph.convert(igraph)
        return igraph


class Vertex:
    def __init__(self, ig_vertex):
        self.ig_vertex = ig_vertex
        self.attributes = dict()
        self.link_edges = set()

    def load(self):
        for key in self.ig_vertex.attribute_names():
            self.attributes[key] = self.ig_vertex[key]

    def display(self, canvas):
        att = self.attributes
        canvas.create_mapped_circle(self, att['x'], att['y'], att['size'], width=att['width'], fill=att['color'], tag=list(att['tag']), activewidth=att['width']+2)

    def visual(self):
        pass
        #print("Vectex: ", self.x, self.y, self.size, self.color, self.width)

    def focus(self, canvas):
        att = self.attributes
        att['color'] = att['focus_color']
        att['tag'].add('highlight')
        self.display(canvas)
        canvas.center_to((att['x'], att['y']))

    def unfocus(self, canvas):
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


class Edge:
    def __init__(self, ig_edge, graph):
        self.ig_edge = ig_edge
        self.points = tuple(map(lambda v: graph.vertices[v], ig_edge.tuple))
        self.points[0].subscribe(self)
        self.points[1].subscribe(self)

    def load(self):
        self.width = self.ig_edge['width']
        self.color = self.ig_edge['color']
        # self.active_color = self.ig_edge['active color']
        self.tag = self.ig_edge['tag']

    def load_point(self):
        self.a = self.points[0].attributes['x']
        self.b = self.points[0].attributes['y']
        self.x = self.points[1].attributes['x']
        self.y = self.points[1].attributes['y']

    def display(self, canvas):
        self.load_point()
        canvas.create_mapped_line(self, self.a, self.b, self.x, self.y, width=self.width, fill=self.color, tag=list(self.tag), activewidth=self.width+1)

    def visual(self):
        print("Edge: ", self.a, self.b, self.x, self.y, self.color, self.width)

    def focus(self, canvas):
        self.color = self.ig_edge['focus_color']
        self.tag.add('highlight')
        self.display(canvas)
        canvas.center_to(((self.a + self.x) / 2, (self.b + self.y) / 2))

    def unfocus(self, canvas):
        self.tag.remove('highlight')
        self.color = self.ig_edge['color']
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



