import numpy as np
import random
import igraph as ig

def test(g2):
    Tb = np.random.normal(2, 0.2**0.5, len(g2.es()))
    Tt = np.random.normal(1, 0.15**0.5, len(g2.es()))
    Tp = np.random.normal(50, 20**0.5, len(g2.es()))
    T = Tb + Tt + Tp
    T[T < 0] = 0
    g2.es["weight"] = T
    min_value = np.amin(T)
    max_value = np.amax(T)
    min_color = (0, 100, 255)
    max_color = (255, 0, 0)
    def val(value, p):
        if min_color[p] == max_color[p]: return str(min_color[p])
        percent = (value - min_value) / (max_value - min_value)
        value = int(min_color[p] + (max_color[p] - min_color[p]) * percent)
        return value
    def rgbr(value):
        return rgb(val(value, 0), val(value, 1), val(value, 2))
    def rgb(r, g, b):
        return "#%02x%02x%02x" % (int(r), int(g), int(b))
    location_color = dict()
    for location in set(g2.vs["GeoLocation"]):
        location_color[location] = rgb(random.uniform(0, 255), random.uniform(0, 255), random.uniform(0, 255))

    g2.vs['size'] = 10
    g2.vs['color'] = [location_color[loc] for loc in g2.vs["GeoLocation"]]
    g2.es['color'] = [rgbr(value) for value in g2.es["weight"]]
    #visual_style["bbox"] = (1800, 1800)

def highlight_shortest_path(g2, path):
    for i in path:
        v = g2.vs[i]
        v['tag'].add('highlight')
        v['size'] = 20
    es = g2.es.select(_between=(path, path))
    for e in es:
        print(e.tuple)
        e['tag'].add('highlight')
        e['width'] = 10

def super_test(canvas):
    import tkinter as tk
    # canvas.pack()
    global photo
    photo = tk.PhotoImage(file="resource//images//pc.png")
    print(photo.width())
    canvas.create_arc(0, 0, 100, 100)
    canvas.create_image(100-photo.width()/2, 100-photo.height()/2, image=photo, anchor=tk.CENTER)
