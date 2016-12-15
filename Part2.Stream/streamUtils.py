def _array_split(points, size):
    start_index = 0
    end_index = size
    arr = []
    while end_index <= len(points):
        arr.append(points[start_index:end_index])
        start_index += size
        end_index += size
    if start_index < len(points):
        arr.append(points[start_index:len(points)])
    return arr;
