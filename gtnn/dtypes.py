from abc import ABC, abstractmethod
from typing import List, Dict


class AbstractGraph(ABC):
    @property
    @abstractmethod
    def nodes(self):
        pass

    @property
    @abstractmethod
    def edges(self):
        pass


def _test_unique(ar: list):
    return len(ar) == len(set(ar))


class MetaGraph(AbstractGraph):
    """
    MetaGraph defines what kind of graph we deal with.
    """

    class EdgeSpec:
        def __init__(self, source: str, target: str, name: str):
            self.source = source
            self.target = target
            self.name = name

    def __init__(self, nodes: List[str], edges: List["MetaGraph.EdgeSpec"]):
        self.__nodes = nodes
        self.__edges = edges

        # index
        self.__node_map: Dict[str, int] = {}
        self.__edge_map_from_source: Dict[str, List[int]] = {}
        self.__edge_map_from_target: Dict[str, List[int]] = {}
        self.__edge_listmap_from: Dict[str, List[str]] = {}
        self.__set_index()

        # test
        self.__test()

    @property
    def nodes(self):
        return self.__nodes

    @property
    def edges(self):
        return self.__edges

    def __set_index(self):
        self.__node_map = {node: i for i, node in enumerate(self.__nodes)}

        # init dict
        self.__edge_map_from_source = {node: [] for node in self.__nodes}
        self.__edge_map_from_target = {node: [] for node in self.__nodes}
        self.__edge_listmap_from = {node: [] for node in self.__nodes}

        # set value
        for i, edge in enumerate(self.__edges):
            self.__edge_map_from_source[edge.source].append(i)
            self.__edge_map_from_target[edge.target].append(i)
            self.__edge_listmap_from[edge.source].append(edge.name)

    def __test(self):
        # test edge boundary
        for edge in self.__edges:
            assert edge.source in self.__nodes
            assert edge.target in self.__nodes

        # test unique name
        for node in self.__nodes:
            assert _test_unique(self.__edge_listmap_from[node])


# example
stdgraph = MetaGraph(
    nodes=["node", "edge"],
    edges=[
        MetaGraph.EdgeSpec("node", "node", "id_node"),
        MetaGraph.EdgeSpec("edge", "edge", "id_edge"),
        MetaGraph.EdgeSpec("node", "edge", "source"),
        MetaGraph.EdgeSpec("node", "edge", "target"),
    ]
)

graph_with_global = MetaGraph(
    nodes=["global", "node", "edge"],
    edges=[
        MetaGraph.EdgeSpec("global", "global", "id_global"),
        MetaGraph.EdgeSpec("node", "node", "id_node"),
        MetaGraph.EdgeSpec("edge", "edge", "id_edge"),
        MetaGraph.EdgeSpec("node", "edge", "source"),
        MetaGraph.EdgeSpec("node", "edge", "target"),
        MetaGraph.EdgeSpec("global", "node", "node_to_global"),
    ]
)


class GenericGraph:
    def __init__(self, meta_graph: MetaGraph):
        self.__meta_graph = meta_graph
        self.__obj_map: dict = {meta_node: [] for meta_node in meta_graph.nodes}
        self.__mor_map: dict = {meta_edge: [] for meta_edge in meta_graph.edges}

    def add(self, meta_node, meta_edge: dict):
        self.__obj_map[meta_node].append(...)  # TODO
