import pytest
from networkx import MultiDiGraph
from pyformlang.cfg import Variable
from project.cfg import CFG
from project.cfpq import cfpq, hellings_closure, matrix


class TestsCFPQ:
    cfg = """
                S -> A B
                S -> A C
                C -> S B
                A -> a
                B -> b
            """
    cfg_info = [
        [
            (0, 1, {"label": "a"}),
            (1, 2, {"label": "a"}),
            (2, 0, {"label": "a"}),
            (2, 3, {"label": "b"}),
            (3, 2, {"label": "b"}),
        ],
        [
            (Variable("A"), 0, 1),
            (Variable("A"), 1, 2),
            (Variable("A"), 2, 0),
            (Variable("B"), 2, 3),
            (Variable("B"), 3, 2),
            (Variable("S"), 1, 3),
            (Variable("C"), 1, 2),
            (Variable("S"), 0, 2),
            (Variable("C"), 0, 3),
            (Variable("S"), 2, 3),
            (Variable("C"), 2, 2),
            (Variable("S"), 1, 2),
            (Variable("C"), 1, 3),
            (Variable("S"), 0, 3),
            (Variable("C"), 0, 2),
            (Variable("S"), 2, 2),
            (Variable("C"), 2, 3),
        ],
    ]
    testdata = [
        (
            cfg,
            cfg_info[0],
            None,
            None,
            cfg_info[1],
            {(1, 2), (0, 3), (2, 3), (0, 2), (2, 2), (1, 3)},
        ),
        (cfg, cfg_info[0], {0, 2}, {3}, cfg_info[1], {(0, 3), (2, 3)}),
    ]

    @pytest.mark.parametrize(
        "cfg, graph_edges, start_nodes, final_nodes, expected_result, expected_cfpq",
        testdata,
    )
    def test_cfpq(
        self,
        cfg,
        graph_edges,
        start_nodes,
        final_nodes,
        expected_result,
        expected_cfpq,
    ):
        cfg = CFG.from_text(cfg)
        graph = MultiDiGraph()
        graph.add_edges_from(graph_edges)
        for alg in {"hellings", "matrix"}:
            res_cfpq = cfpq(cfg, graph, start_nodes, final_nodes, alg_type=alg)
            res_alg = (
                hellings_closure(cfg, graph)
                if alg == "hellings"
                else matrix(cfg, graph)
            )
            assert res_cfpq == expected_cfpq
            assert set(res_alg) == set(expected_result)
