"""
truck called functions
"""
from functools import wraps
from typing import List, Tuple

from gtnn.dtypes import AbstractGraph


class CallPoint:
    """
    check which functions are called as a tree format

    >>> cp = CallPoint()
    >>> @cp
        def a(): b()
    >>> @cp
        def b(): c()
    >>> @cp
        def c(): pass

    >>> fg = FunctionGraphBuilder([cp])
    >>> a()
    >>> print(fg.build())
    """

    def __init__(self):
        self.__functions = []
        self.__builders = []

    def __call__(self, fn):
        index = len(self.__functions)
        self.__functions.append(fn)

        @wraps(fn)
        def wrapper(*args, **kwargs):
            for builder in self.__builders:
                builder.enter(self, index)

            result = fn(*args, **kwargs)

            for builder in self.__builders:
                builder.exit(self)

            return result

        return wrapper

    def add_builder(self, builder):
        """
        add builder
        """
        self.__builders.append(builder)


class FunctionGraphBuilder:
    """

    """

    def __init__(self, cps: List[CallPoint]):
        self.__nodes: List[Tuple[CallPoint, int]] = []
        self.__edges: List[Tuple[CallPoint, CallPoint]] = []
        self.__cps = cps
        self.__cp_to_index = {cp: i for i, cp in enumerate(cps)}
        self.__path: List[CallPoint] = []
        self.__count = 0

        for cp in cps:
            cp.add_builder(self)

    def build(self):
        """
        build graph
        """
        nodes = [(self.__cp_to_index[cp], i) for cp, i in self.__nodes]
        edges = [(self.__cp_to_index[node_from], self.__cp_to_index[node_to]) for node_from, node_to in self.__edges]
        return FunctionGraph(nodes=nodes, edges=edges)

    def enter(self, cp: CallPoint, index: int):
        """
        enter callpoint
        """
        if cp not in self.__cps:
            return

        self.__path.append(cp)
        self.__nodes.append((cp, index))
        if len(self.__path) > 1:
            self.__edges.append((self.__path[-2], self.__path[-1]))

    def exit(self, cp: CallPoint):
        """
        exit callpoint
        """
        if cp not in self.__cps:
            return
        self.__path.pop()


class FunctionGraph(AbstractGraph):
    def __init__(self, nodes, edges):
        super()
        self.__nodes = nodes
        self.__edges = edges

    @property
    def nodes(self):
        return self.nodes

    @property
    def edges(self):
        return self.__edges
