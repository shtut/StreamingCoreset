"""
Defines the message class used in socket communication
"""
class Message(object):
    def __init__(self, code, points=None):
        self.code = code
        self.points = points
