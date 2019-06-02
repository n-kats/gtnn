"""
export gtnn graph to networkx
"""
import networkx as nx
from gtnn.dtypes import AbstractGraph


def to_networkx(graph: AbstractGraph) -> nx.MultiDiGraph:
    g_out = nx.MultiDiGraph()
    for node in graph.nodes:
        g_out.add_node(node)
    for edge in graph.edges:
        g_out.add_edge(edge.source, edge.target)
    return g_out


def preview(graph, **kwargs):
    nx.nx_agraph.view_pygraphviz(graph, **kwargs)
