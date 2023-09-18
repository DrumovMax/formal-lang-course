from typing import Set

from networkx import MultiDiGraph
from pyformlang.regular_expression import *
from pyformlang.finite_automaton import *


def create_minimal_dfa(regex: Regex) -> DeterministicFiniteAutomaton:
    """Creates a minimal DFA by a given regular expression.

    Parameters:
    ------------
    regex: Regex
        Regular expression by which the DFA will be built.
    Return:
    ------------
    DeterministicFiniteAutomaton
        Created minimized DFA.
    """
    return regex.to_epsilon_nfa().to_deterministic().minimize()


def create_nfa(
    graph: MultiDiGraph, start_states: Set[int] = None, final_states: Set[int] = None
) -> NondeterministicFiniteAutomaton:
    """Creates NFA by a given graph.

    Parameters:
    ------------
    graph: MultiDiGraph
        The graph on which the NFA will be constructed.
    start_states: Set[int]
        Starting states of the automaton.
    final_states: Set[int]
        Final states of the automaton.
    Return:
    ------------
    NondeterministicFiniteAutomaton
        Created NFA.
    """
    nfa = NondeterministicFiniteAutomaton()

    for edge in graph.edges(data=True):
        nfa.add_transition(State(edge[0]), Symbol(edge[2]["label"]), State(edge[1]))

    if start_states is None and final_states is None:
        for state in nfa.states:
            nfa.add_start_state(state)
            nfa.add_final_state(state)

    if start_states is not None:
        for state in start_states:
            nfa.add_start_state(State(state))

    if final_states is not None:
        for state in final_states:
            nfa.add_final_state(State(state))

    return nfa
