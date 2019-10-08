import math
import numpy as np
def distance(a,b):
    return sqrt((a.x - b.x)**2 + (a.y - b.y)**2)

def is_between(a,c,b):
    return math.fabs(distance(a,c) + distance(c,b) - distance(a,b)) < 0.0001

def get_lines_intersect(a1, a2, b1, b2):
    s = np.vstack([a1,a2,b1,b2])        # s for stacked
    h = np.hstack((s, np.ones((4, 1)))) # h for homogeneous
    l1 = np.cross(h[0], h[1])           # get first line
    l2 = np.cross(h[2], h[3])           # get second line
    x, y, z = np.cross(l1, l2)          # point of intersection
    if z == 0:                          # lines are parallel
        return (float('inf'), float('inf'))
    return (x/z, y/z)

def segments_are_collided(a1, a2, b1, b2):
    point = np.array(get_lines_intersect(a1, a2, b1, b2))
    if (point == (float('inf'), float('inf'))).any(): return (a1 == b1).all() or (a2 == b2).all()
    else: return is_between(a1, point, a2) and is_between(b1, point, b2)

def point_is_inside_rect(point, top_left, bottom_right):
    return np.logical_and(point >= top_left, point <= bottom_right).all()

def segments_are_collided_rect(a1, a2, top_left, bottom_right):
    return  segments_are_collided(a1, a2, (top_left[0], bottom_right[0]), (top_left[1], bottom_right[0])) \
        or segments_are_collided(a1, a2, (top_left[1], bottom_right[0]), (top_left[1], bottom_right[1])) \
        or segments_are_collided(a1, a2, (top_left[1], bottom_right[1]), (top_left[0], bottom_right[1])) \
        or segments_are_collided(a1, a2, (top_left[0], bottom_right[1]), (top_left[0], bottom_right[0]))
