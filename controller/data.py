from visual import vgraph, vcanvas

# TODO edit data here


class Controller:
    __instance = None
    __graph = None
    __canvas = None
    @staticmethod
    def get_instance():
        if not Controller.__instance:
            Controller.__instance = Controller()
        return Controller.__instance

    def get_graph(self):
        return self.__graph

    def load(self, instance, canvas, **kwargs):
        # TODO add more type
        self.__canvas = canvas
        vcanvas.Canvas.convert(canvas)
        g = self.__graph = vgraph.Graph()
        g.add_vertex(type='pc', name='pc1', x=0, y=0)
        g.add_vertex(type='pc', name='pc2', x=0, y=-10)
        g.add_vertex(type='pc', name='pc3', x=0, y=10)
        g.add_vertex(type='switch', name='switch', x=10, y=0)
        g.add_edge('switch', 'pc1')
        g.add_edge('switch', 'pc2')
        g.add_edge('switch', 'pc3')
        # g.load()
        g.fit_canvas(canvas)
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

    def subscribe_labels(self, label_x, label_y):
        self.__canvas.subscriber['label_x'] = label_x
        self.__canvas.subscriber['label_y'] = label_x



