import pytest
from networkx import MultiDiGraph
from project.cfg import CFG
from project.cfpq import cfpq


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
    ]
    testdata = [
        (
            cfg,
            cfg_info[0],
            None,
            None,
            {(1, 2), (0, 3), (2, 3), (0, 2), (2, 2), (1, 3)},
        ),
        (cfg, cfg_info[0], {0, 2}, {3}, {(0, 3), (2, 3)}),
    ]

    @pytest.mark.parametrize(
        "cfg, graph_edges, start_nodes, final_nodes, expected_cfpq",
        testdata,
    )
    def test_cfpq(
        self,
        cfg,
        graph_edges,
        start_nodes,
        final_nodes,
        expected_cfpq,
    ):
        cfg = CFG.from_text(cfg)
        graph = MultiDiGraph()
        graph.add_edges_from(graph_edges)
        for alg in {"hellings", "matrix", "tensor"}:
            res_cfpq = cfpq(cfg, graph, start_nodes, final_nodes, alg_type=alg)
            assert res_cfpq == expected_cfpq
