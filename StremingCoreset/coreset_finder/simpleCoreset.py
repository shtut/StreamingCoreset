import random

class SimpleCoreset:
    """
    contains a simple coreset algorithm - return a random portion of the data
    In size of coreSetSize
    """
    def __init__(self, p):
        self._points = p

    @staticmethod
    def coreset_alg(p, w):
        return SimpleCoreset(p)

    def sample(self, coreSetSize):
        x = random.sample(self._points, coreSetSize)
        return x, None
