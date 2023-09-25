from networkx import MultiDiGraph
from project.rpq import rpq
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
