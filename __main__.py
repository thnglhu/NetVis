from visual import vgraph, vcanvas
import tkinter as tk
import test

if __name__ == '__main__':

    graph = vgraph.read("sample/NREN.graphml")
    # graph = vgraph.Graph.Full(5)
    # graph.vs['x'] = [1, 2, 3]
    # graph.vs['y'] = [2, 3, 4, 5, 6, 7, 8]
    # graph.es['size'] = 5
    

    root = tk.Tk()

    canvas = vcanvas.Canvas(root, width=800, height=700)
    canvas.pack()

    # from threading import Thread

    graph.vs['color'] = 'red'
    graph.fit_canvas(canvas)

    test.test(graph)

    path = graph.get_shortest_paths(0, 332)[0]

    test.highlight_shortest_path(graph, path)
    # graph.convex_hull(shortest_paths)


    # canvas.lift('vertex')
    # canvas.lower('edge')
    # canvas.lift('vertex-highlight')

    graph.load()
    graph.display(canvas)
    # graph.load()
    # graph.display(canvas)

   # root = tk.Tk()
   # root.geometry("400x300")
   # from visual import window as w
   # app = w.Window(root)
    tk.mainloop()
