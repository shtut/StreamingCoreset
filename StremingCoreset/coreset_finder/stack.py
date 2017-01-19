import copy


class Stack:
    """
    utility class implementing a stack
    """
    def __init__(self):
        self._items = []

    def is_empty(self):
        return self.size() == 0

    def push(self, item):
        self._items.append(item)

    def pop(self):
        return self._items.pop()

    def size(self):
        return len(self._items)

    def top(self):
        return self._items[len(self._items) - 1]

    def list(self):
        return copy.copy(self._items)
