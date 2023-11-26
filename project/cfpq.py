from networkx import MultiDiGraph
from pyformlang.cfg import CFG, Variable
from scipy.sparse import dok_array, eye
from project.cfg import cfg_to_wcnf


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
    for start and final nodes of your graph using the Helling`s or Matrix algorithms.

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
