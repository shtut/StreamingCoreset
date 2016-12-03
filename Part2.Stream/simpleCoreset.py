class CoreSetHandler:
    def __init__(self, p):
        self._points = p

    @staticmethod
    def coreset_alg(p, unknow, num1, num2):
        return CoreSetHandler(p)

    def sample(self, coreSetSize):
        return self._points[0:coreSetSize], None
