from networkx import MultiDiGraph
from project.rpq import rpq, bfs_rpq
from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import State


class TestsForRpq:
    def test_graph(self):
        graph = MultiDiGraph()
        graph.add_edges_from(
            [
                (0, 1, {"label": "R"}),
                (1, 2, {"label": "P"}),
                (2, 3, {"label": "Q"}),
                (3, 4, {"label": "G"}),
                (4, 5, {"label": "R"}),
            ]
        )

        return graph

    def test_not_degenerated_case(self):
        graph = self.test_graph()
        regex = Regex("R P Q")

        assert rpq(regex, graph, {State(0)}, {State(3)}) == {(0, 3)}

    def test_empty_regex(self):
        graph = self.test_graph()
        regex = Regex("")

        assert rpq(regex, graph) == set()

    def test_graph_for_bfs_rpq(self):
        graph = MultiDiGraph()
        nodes = [0, 1, 2, 3, 4, 5, 6]
        graph.add_edges_from(
            [
                (nodes[0], nodes[1], {"label": "a"}),
                (nodes[1], nodes[2], {"label": "b"}),
                (nodes[2], nodes[3], {"label": "a"}),
                (nodes[3], nodes[4], {"label": "b"}),
                (nodes[0], nodes[2], {"label": "a"}),
                (nodes[2], nodes[5], {"label": "b"}),
                (nodes[3], nodes[6], {"label": "a"}),
                (nodes[6], nodes[0], {"label": "b"}),
            ]
        )

        return graph

    def test_bfs_rpq(self):
        regex = Regex("b*.a.b")
        graph = MultiDiGraph()
        nodes = [0, 1, 2, 3]
        graph.add_edges_from(
            [
                (nodes[0], nodes[1], {"label": "a"}),
                (nodes[0], nodes[3], {"label": "b"}),
                (nodes[3], nodes[0], {"label": "b"}),
                (nodes[1], nodes[2], {"label": "b"}),
                (nodes[2], nodes[0], {"label": "a"}),
            ]
        )

        result = bfs_rpq(regex, graph, {0, 1}, {2}, True)
        assert result == {(nodes[0], nodes[2]), (nodes[1], nodes[2])}

    def test_full_bfs_rpq(self):
        regex = Regex("(a|b)*")
        graph = self.test_graph_for_bfs_rpq()
        nodes = [0, 1, 2, 3, 4, 5, 6]

        result = bfs_rpq(regex, graph)
        assert result == set(nodes)

    def test_empty_regex_bfs_rpq(self):
        regex = Regex("")
        graph = self.test_graph_for_bfs_rpq()

        assert bfs_rpq(regex, graph, is_separate=True) == set()
        assert bfs_rpq(regex, graph, is_separate=False) == set()

    def test_empty_graph_bfs_rpq(self):
        graph = MultiDiGraph()
        assert bfs_rpq(Regex("Tyler"), graph, is_separate=True) == set()
        assert bfs_rpq(Regex("Derden"), graph, is_separate=False) == set()
