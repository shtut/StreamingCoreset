import numpy as np


def array_split(points, size):
    """

    :param points:
    :param size:
    :return:
    """
    start_index = 0
    end_index = size
    arr = []
    while end_index <= len(points):
        arr.append(points[start_index:end_index])
        start_index += size
        end_index += size
    if start_index < len(points):
        arr.append(points[start_index:len(points)])
    return arr


def convert_points_to_float(matrix):
    """
    converts a given matrix to float
    :param matrix: a matrix
    :return: float matrix
    """
    res = None
    for line in matrix:
        new_line = []
        for v in line:
            new_line.append(float(v))
        if res is None:
            res = new_line
        else:
            res = np.vstack([res, np.asanyarray(new_line)])
    return res
