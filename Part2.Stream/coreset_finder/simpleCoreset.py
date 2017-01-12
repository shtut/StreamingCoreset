class SimpleCoreset:
    """
    contains a simple coreset algorithm - return only the first part of the data,  in coreset size (first p points)
    used for testing
    """
    def __init__(self, p):
        self._points = p

    @staticmethod
    def coreset_alg(p, w):
        return SimpleCoreset(p)

    def sample(self, coreSetSize):
        return self._points[0:coreSetSize], None
