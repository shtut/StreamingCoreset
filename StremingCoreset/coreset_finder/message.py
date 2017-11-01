"""
Defines the message class used in socket communication
"""


class Message(object):
    def __init__(self, code, points=None, weights=None):
        self.code = code
        self.points = points
        self.weights = weights
