from . import data
import os

# TODO edit application here


class Controller:
    __instance = None

    @staticmethod
    def get_instance():
        if not Controller.__instance:
            Controller.__instance = Controller()
        return Controller.__instance

    def __init__(self):
        self.__controller = data.Controller.get_instance()

    def load(self, file, canvas):
        _, extension = os.path.splitext(file.name)
        self.__controller.load(file, canvas, extension=extension[1:])
        graph = self.__controller.get_graph()


    def exit(self):
        pass

    def filter(self, **kwargs):
        # filter(target="vertex", criteria="GeoLocation", equal="USA")
        target = kwargs.get("target")
        criteria = kwargs.get("criteria")
        equal = kwargs.get("equal")
        if target == "edge":
            pass
        elif target == "vertex":
            graph = self.__controller.get_graph()
            graph.vs["activate"] = [True if v[criteria] == equal else False for v in graph.vs]
            pass
        else:
            raise TypeError

    def bind(self, *cnf, **kwargs):
        if kwargs.get("canvasposition"):
            label_x = cnf[0]
            label_y = cnf[1]
            self.__controller.subscribe_labels(label_x, label_y)
        else:
            raise NotImplementedError

    def test(self):
        self.__controller.test()
