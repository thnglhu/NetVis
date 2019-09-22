import numpy as np
import random as rd


def transform(value, value_range, value2_range):
    value_range = np.array(value_range)
    value2_range = np.array(value2_range)
    if value_range[0] == value_range[1]: return rd.uniform(*value2_range)
    else:
        percent = (value - value_range[0]) / (value_range[1] - value_range[0])
        return value2_range[0] + (value2_range[1] - value2_range[0]) * percent
