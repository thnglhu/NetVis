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
        self.__graph = vgraph.Graph.Full(10)
        vs = self.__graph.get_vs()
        self.__graph.load()
        print(vs.items)
        vs['x'] = [1, -3]
        vs['y'] = [1, 3, 5, 7, 5]
        self.__graph.fit_canvas(canvas)
        self.__graph.display(canvas)
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



