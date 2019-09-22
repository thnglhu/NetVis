from PyQt4.QtGui import *
from PYQT.visual import vgraph

"""
class Vertex(QGraphicsEllipseItem):
    def __init__(self, position):
        super(Vertex, self).__init__(-rad, -rad, 2*rad, 2*rad)

        self.rad = rad
        self.setPos(position[0], position[1])
        self.linkedEdges = set()
        self.setZValue(2)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setBrush(Qt.green)

    def itemChange(self, change, value):
        r = QGraphicsEllipseItem.itemChange(self, change, value)
        if change == QGraphicsItem.ItemPositionChange:
            self.position = self.pos().x(), self.pos().y()
            for edge in self.linkedEdges:
                edge.updateElement()
            # self.path.updateElement(self.index, value)
        return r

    def subscribe(self, edge):
        self.linkedEdges.add(edge)


class Edge(QGraphicsLineItem):
    def __init__(self, A, B):
        self.A, self.B = A, B
        A.subscribe(self)
        B.subscribe(self)
        pos_a = A.pos().x(), A.pos().y()
        pos_b = B.pos().x(), B.pos().y()
        super(Edge, self).__init__(*pos_a, *pos_b)
        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setPen(QPen(QColor("red"), 5))

    def updateElement(self):
        pos_a = A.pos().x(), A.pos().y()
        pos_b = B.pos().x(), B.pos().y()
        self.setLine(*pos_a, *pos_b)
        """


if __name__ == "__main__":

    app = QApplication([])
    # path = QPainterPath()
    # path.moveTo(0,0)
    # path.cubicTo(-30, 70, 35, 115, 100, 100);
    # path.lineTo(200, 100);
    # path.cubicTo(200, 30, 150, -35, 60, -30);
    # path.lineTo(300, 200)

    scene = QGraphicsScene()
    graph = vgraph.read("sample/NREN.graphml", scene)
    # scene.addItem(Path(path, scene))

    view = QGraphicsView(scene)
    view.setDragMode(QGraphicsView.ScrollHandDrag)
    view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
    view.setRenderHint(QPainter.Antialiasing)
    view.resize(600, 400)
    view.show()
    app.exec_()