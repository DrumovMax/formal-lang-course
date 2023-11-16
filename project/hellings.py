from typing import List, Tuple, Any

from networkx import MultiDiGraph
from pyformlang.cfg import CFG, Variable, Terminal
from project.cfg import cfg_to_wcnf, get_cfg_from_file
from project.graph_utils import load_graph


def hellings_closure(cfg: CFG, graph: MultiDiGraph):
    """Find transitive closure of the graph with constraints of cfg grammar.

    Parameters:
    ----------
    cfg: CFG
        Context-free grammar.
    graph: MultiDiGraph
        A directed graph class.
    Returns:
    -------
    result: set
        Result is set of triples of the form (node, non-terminal, node)
    """
    cfg = cfg_to_wcnf(cfg)
    term_prod = {prod for prod in cfg.productions if len(prod.body) == 1}
    var_prod = {prod for prod in cfg.productions if len(prod.body) == 2}
    eps_prod = {prod for prod in cfg.productions if len(prod.body) > 2}
    result = []
    for (v, j, label) in graph.edges(data="label"):
        for prod in term_prod:
            if label == prod.body[0].value:
                result.append((prod.head, v, j))
    for n in graph.nodes:
        for prod in eps_prod:
            result.append((prod.head, n, n))
    m = result.copy()
    while m:
        i, v, j = m.pop()
        for (i_r, v_r, j_r) in result:
            if v == j_r:
                for prod in var_prod:
                    closure = (prod.head, v_r, j)
                    if (
                        prod.body[0] == i_r
                        and prod.body[1] == i
                        and closure not in result
                    ):
                        result.append(closure)
                        m.append(closure)
        for (i_r, v_r, j_r) in result:
            if j == v_r:
                for prod in var_prod:
                    closure = (prod.head, v, j_r)
                    if (
                        prod.body[0] == i
                        and prod.body[1] == i_r
                        and closure not in result
                    ):
                        result.append(closure)
                        m.append(closure)
    return result


def cfpq(
    cfg: CFG,
    graph: MultiDiGraph,
    start_nodes: set = None,
    final_nodes: set = None,
    start_symbol: Variable = Variable("S"),
):
    """
    It allows you to solve a reachability problem
    for start and final nodes of your graph using the Helling`s algorithm.

    Parameters:
    ----------
    cfg: CFG
        Context-free grammar.
    graph: MultiDiGraph
        A directed graph class.
    start_nodes: set | None
        This is set of start nodes of the graph
    final_nodes: set | None
        This is set of final nodes of the graph
    start_symbol: Variable
        Start symbol of CFG
    Returns:
    -------
    result: set
        Result is a set of pairs of nodes
    """
    if start_nodes is None:
        start_nodes = graph.nodes
    if final_nodes is None:
        final_nodes = graph.nodes

    return {
        (v, j)
        for i, v, j in hellings_closure(cfg, graph)
        if i == start_symbol and v in start_nodes and j in final_nodes
    }
