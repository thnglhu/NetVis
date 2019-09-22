import igraph as ig
from PyQt4.QtGui import *
from PyQt4.QtCore import *


def read(filename, master=None, *args, **kwargs):
    graph = ig.read(filename, *args, **kwargs)
    Graph.convert(graph, master)
    return graph


def load(source, target):
    for key in source:
        target[key] = source[key]


class Graph(ig.Graph):
    def __init__(self, master=None, *args, **kwargs):
        ig.Graph.__init__(self, *args, **kwargs)
        self._init_subclass(master)

    def _init_subclass(self, master):
        self.master = master

        def shorten(element, attributes, *key_default):
            for pair in key_default:
                element[pair[0]] = attributes.get(pair[0], pair[1]) or pair[1]

        for i, v in enumerate(self.vs):
            va = v.attributes()
            keys = ['x', 'y', 'size', 'width', 'color', 'tag', 'index', 'state', 'focus_color']
            defaults = [0, 0, 10, 2, 'red', '    vertex', i, 'normal', 'pink']
            shorten(v, va, *zip(keys, defaults))
        self.vertices = list(map(lambda v: Vertex(v), self.vs))

        for i, e in enumerate(self.es):
            ea = e.attributes()
            keys = ['width', 'color', 'tag', 'focus_color']
            defaults = [2, 'black', 'edge', 'gray']
            shorten(e, ea, *zip(keys, defaults))
        self.edges = list(map(lambda e: Edge(e), self.es))
        for e in self.vertices:
            master.addItem(e)
        for v in self.edges:
            master.addItem(v)
        # .threads = [None] * 10

    @classmethod
    def convert(cls, igraph, master):
        igraph.__class__ = Graph
        igraph._init_subclass(master)
        return igraph

    @classmethod
    def Full(cls, n, master=None, directed=False, loops=False):
        igraph = ig.Graph.Full(n, directed, loops)
        Graph.convert(igraph, master)
        return igraph


class Vertex(QGraphicsEllipseItem):
    def __init__(self, ig_vertex):
        self.ig_vertex = ig_vertex
        self.attributes = dict()
        load(ig_vertex.attributes(), self.attributes)
        radius = self.attributes['size']
        super(Vertex, self).__init__(-radius, -radius, 2*radius, 2*radius)

        self.setPos(self.attributes['x'], self.attributes['y'])
        self.linkedEdges = set()
        self.setZValue(2)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setBrush(QColor(self.attributes['color']))

    def itemChange(self, change, value):
        r = QGraphicsEllipseItem.itemChange(self, change, value)
        if change == QGraphicsItem.ItemPositionChange:
            for edge in self.linkedEdges:
                edge.updateElement()
            # self.path.updateElement(self.index, value)
        return r

    def subscribe(self, edge):
        self.linkedEdges.add(edge)


class Edge(QGraphicsLineItem):
    def __init__(self, ig_edge):
        self.ig_edge = ig_edge
        self.attributes = dict()
        load(ig_edge.attributes(), self.attributes)
        graph = ig_edge.graph
        self.end_a = graph.vertices[ig_edge.tuple[0]]
        self.end_b = graph.vertices[ig_edge.tuple[1]]
        self.end_a.subscribe(self)
        self.end_b.subscribe(self)
        super(Edge, self).__init__(self.end_a.pos().x(), self.end_a.pos().y(), self.end_b.pos().x(), self.end_b.pos().y())

        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setPen(QPen(QColor(self.attributes['color']), self.attributes['width']))

    def updateElement(self):
        self.setLine(self.end_a.pos().x(), self.end_a.pos().y(), self.end_b.pos().x(), self.end_b.pos().y())


"""
class Vertex(QGraphicsEllipseItem):
    def __init__(self, ig_vertex):
        self.ig_vertex = ig_vertex
        self.attributes = dict()
        load(self.ig_vertex.attribute_names(), self.attributes)
        radius = self.attributes['size']
        super(Vertex, self).__init__(-radius, -radius, 2*radius, 2*radius)
        # self.setFlag(QGraphicsItem.ItemIsMovable)
        # self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)


    # def display(self, canvas):
    #    att = self.attributes
    #    canvas.create_mapped_circle(self, att['x'], att['y'], att['size'], width=att['width'], fill=att['color'], tag=att['tag'], activewidth=att['width']+2)

    def visual(self):
        pass
        #print("Vectex: ", self.x, self.y, self.size, self.color, self.width)
    def focus(self, canvas):
        att = self.attributes
        att['color'] = att['focus_color']
        self.display(canvas)
        canvas.center_to((att['x'], att['y']))
    def unfocus(self, canvas):
        att = self.attributes
        att['color'] = self.ig_vertex['color']
        att['focus_size'] = self.ig_vertex['size']
        self.display(canvas)
    def graph(self):
        return self.ig_vertex.graph
    def motion(self, canvas, delta_x, delta_y):
        print(self.attributes['x'], self.attributes['y'], delta_x, delta_y)
        self.attributes['x'] += delta_x
        self.attributes['y'] += delta_y
        print(self.attributes['x'], self.attributes['y'])
        self.display(canvas)
        for edge in self.link_edges: edge.display(canvas)
        print(len(self.link_edges))
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
        #self.active_color = self.ig_edge['active color']
        self.tag = self.ig_edge['tag']
    def load_point(self):
        self.a = self.points[0].attributes['x']
        self.b = self.points[0].attributes['y']
        self.x = self.points[1].attributes['x']
        self.y = self.points[1].attributes['y']
    def display(self, canvas):
        self.load_point()
        canvas.create_mapped_line(self, self.a, self.b, self.x, self.y, width=self.width, fill=self.color, tag=self.tag, activewidth=self.width+1)
    def visual(self):
        print("Edge: ", self.a, self.b, self.x, self.y, self.color, self.width)
    def focus(self, canvas):
        self.color = self.ig_edge['focus_color']
        self.display(canvas)
        canvas.center_to(((self.a + self.x) / 2, (self.b + self.y) / 2))
    def unfocus(self, canvas):
        self.color = self.ig_edge['color']
        self.display(canvas)
    def graph(self):
        return self.ig_edge.graph
"""