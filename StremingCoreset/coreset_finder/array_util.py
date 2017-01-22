import numpy as np


def array_split(points, size):
    """
    given an array 'points', splits into smaller arrays of size 'size'
    i.e. [1,2,3,4,5,6,7,8,9,10] with size=2  => [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]]
    :param points: original array
    :param size: requested size of smaller arrays
    :return: an array containing smaller arrays of size='size'
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
