from networkx import MultiDiGraph
from pyformlang.cfg import CFG, Variable
from scipy.sparse import dok_array, eye, lil_matrix

from project.bool_matrix import BoolMatrix
from project.cfg import cfg_to_wcnf
from project.ecfg import ECFG
from project.fa_utils import create_nfa
from project.rsm import RSM


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
    alg_type: str = "hellings",
):
    """
    It allows you to solve a reachability problem
    for start and final nodes of your graph
    using the Helling`s, Tensor or Matrix algorithms.

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
        for i, v, j in (
            hellings_closure(cfg, graph)
            if alg_type == "hellings"
            else matrix(cfg, graph)
            if alg_type == "matrix"
            else tensor(cfg, graph)
        )
        if i == start_symbol and v in start_nodes and j in final_nodes
    }


def matrix(cfg: CFG, graph: MultiDiGraph):
    """Find transitive closure of the graph with constraints of cfg grammar.

    Parameters:
    ----------
    graph : MultiDiGraph
        Input graph from networkx.
    cfg : CFG
        Context-Free Grammar.
    Returns:
    -------
    res : Set
        Constrained transitive closure of graph.
    """
    cfg = cfg_to_wcnf(cfg)
    term_prod = {prod for prod in cfg.productions if len(prod.body) == 1}
    var_prod = {prod for prod in cfg.productions if len(prod.body) == 2}
    eps_prod = {prod for prod in cfg.productions if len(prod.body) > 2}

    size = len(graph.nodes)
    adjs = {v: dok_array((size, size), dtype=bool) for v in cfg.variables}
    nodes = {n: i for i, n in enumerate(graph.nodes)}

    for (v, u, label) in graph.edges(data="label"):
        for prod in term_prod:
            if label == prod.body[0].value:
                adjs[prod.head][nodes[v], nodes[u]] = True

    for adj in adjs.values():
        adj.tocsr()

    diag = eye(len(nodes), dtype=bool, format="csr")
    for v in eps_prod:
        adjs[v.head] += diag

    changing = True
    while changing:
        changing = False
        for prod in var_prod:
            nnz_old = adjs[prod.head].nnz
            adjs[prod.head] += adjs[prod.body[0]] @ adjs[prod.body[1]]
            changing |= adjs[prod.head].nnz != nnz_old

    nodes = {i: n for n, i in nodes.items()}
    r = []
    for N, adj in adjs.items():
        nz = adj.nonzero()
        for i, j in list(zip(nz[0], nz[1])):
            r.append((N, nodes[i], nodes[j]))
    return r


def tensor(cfg: CFG, graph: MultiDiGraph):
    """
    Solves the reachability problem via the tensor algorithm

    Parameters:
    ----------
    cfg : CFG
        Context-Free Grammar.
    graph : MultiDiGraph
        Input graph from networkx.
    Returns:
    -------
    res : Set
        Constrained transitive closure of graph.
    """
    bmatrix_rsm = BoolMatrix(
        RSM.ecfg_to_rsm(ECFG.ecfg_from_cfg(cfg)).minimize().merge_boxes_to_nfa()
    )
    bm_rsm_i_st = {i: st for st, i in bmatrix_rsm.states_dict.items()}

    bmatrix_graph = BoolMatrix(create_nfa(graph))
    bm_g_i_st = {i: st for st, i in bmatrix_graph.states_dict.items()}

    identity_matrix = eye(bmatrix_graph.states_amount, format="dok", dtype=bool)
    for nonterm in cfg.get_nullable_symbols():
        if nonterm.value in bmatrix_graph.bool_matrix.keys():
            bmatrix_graph.bool_matrix[nonterm.value] += identity_matrix
        else:
            bmatrix_graph.bool_matrix[nonterm.value] = identity_matrix

    index_len = 0
    while True:
        tc_indexes = list(
            zip(*bmatrix_rsm.intersect(bmatrix_graph).transitive_closure().nonzero())
        )
        if len(tc_indexes) == index_len:
            break
        index_len = len(tc_indexes)

        for (i, j) in tc_indexes:
            r_i, g_i = divmod(i, bmatrix_graph.states_amount)
            r_j, g_j = divmod(j, bmatrix_graph.states_amount)

            state_from = bm_rsm_i_st[r_i]
            state_to = bm_rsm_i_st[r_j]
            nonterm, _ = state_from.value
            if (
                state_from in bmatrix_rsm.start_states
                and state_to in bmatrix_rsm.final_states
            ):
                if nonterm.value in bmatrix_graph.bool_matrix.keys():
                    bmatrix_graph.bool_matrix[nonterm][g_i, g_j] = True
                else:
                    bmatrix_graph.bool_matrix[nonterm] = lil_matrix(
                        (
                            bmatrix_graph.states_amount,
                            bmatrix_graph.states_amount,
                        ),
                        dtype=bool,
                    )
                    bmatrix_graph.bool_matrix[nonterm][g_i, g_j] = True
    return {
        (
            nonterm,
            bm_g_i_st[graph_i],
            bm_g_i_st[graph_j],
        )
        for nonterm, mtx in bmatrix_graph.bool_matrix.items()
        for graph_i, graph_j in zip(*mtx.nonzero())
    }
