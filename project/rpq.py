from networkx import MultiDiGraph
from pyformlang.regular_expression import Regex
from project.bool_matrix import BoolMatrix
from project.fa_utils import create_minimal_dfa, create_nfa


def rpq(
    regex: Regex,
    graph: MultiDiGraph,
    start_nodes: set = None,
    final_nodes: set = None,
):
    """
    Perform regular queries on graphs.

    Parameters
    ----------
    regex : Regex
        Regular expression from pyformlang.
    graph : MultiDiGraph
        Graph from networkx.
    start_nodes : set
        Start states of finite automaton.
    final_nodes : set
        Final states of finite automaton.
    Returns
    -------
    result : any
        Returns pairs of nodes from the given start and end nodes
        that are connected by a path generated using regex.
    """
    graph_fa = create_nfa(graph, start_nodes, final_nodes)
    regex_fa = create_minimal_dfa(regex)

    graph_bm = BoolMatrix(graph_fa)
    regex_bm = BoolMatrix(regex_fa)

    intersection = graph_bm.intersect(regex_bm)

    start_states = intersection.start_states
    final_states = intersection.final_states

    result = {
        (first // regex_bm.states_amount, second // regex_bm.states_amount)
        for first, second in zip(*intersection.transitive_closure().nonzero())
        if first in start_states and second in final_states
    }

    return result


def bfs_rpq(
    regex: Regex,
    graph: MultiDiGraph,
    start_nodes: set = None,
    final_nodes: set = None,
    is_separate: bool = False,
):
    """
    Perform regular queries on graphs.

    Parameters
    ----------
    regex : Regex
        Regular expression from pyformlang.
    graph : MultiDiGraph
        Graph from networkx.
    start_nodes : set
        Start states of finite automaton.
    final_nodes : set
        Final states of finite automaton.
    is_separate : bool
        Flag represented type of solving problem
    Returns
    -------
    result : any
        Returns either a set of reachable states, or a set of state pairs where the first element is responsible
        for the initial state and the second element is responsible for the final state. pairs of states,
        where the first element is responsible for the initial state and the second for the final state.
    """
    graph_fa = create_nfa(graph, start_nodes, final_nodes)
    regex_fa = create_minimal_dfa(regex)

    graph_bm = BoolMatrix(graph_fa)
    regex_bm = BoolMatrix(regex_fa)

    result = graph_bm.constraint_bfs(regex_bm, is_separate)

    return result
