class NodoDoble:
    __slots__ = '_elemento', '_anterior', '_siguiente'
    def __init__(self, elemento=None, anterior=None, siguiente=None):
        self._elemento = elemento
        self._anterior = anterior
        self._siguiente = siguiente
