import unittest

from gtnn.dtypes import MetaGraph


class GraphTest(unittest.TestCase):
    def test_gragh(self):
        graph = MetaGraph(
            nodes=["A", "B"],
            edges=[
                MetaGraph.EdgeSpec("A", "B", "source"),
                MetaGraph.EdgeSpec("A", "B", "target"),
            ],
        )

        self.assertEqual(graph.nodes, ["A", "B"])
