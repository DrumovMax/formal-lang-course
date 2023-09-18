from networkx import MultiDiGraph
from project.graph_utils import *
from project.fa_utils import *


class TestsFAUtils:
    def test_create_minimal_deterministic_automata(self):
        regex = Regex("")
        minimal_dfa = create_minimal_dfa(regex)
        assert minimal_dfa.is_deterministic()
        assert minimal_dfa.is_empty()

        regex_concatenate = regex.concatenate(Regex("a"))
        minimal_dfa = create_minimal_dfa(regex_concatenate)
        minimize_dfa = minimal_dfa.minimize()
        assert minimal_dfa.is_equivalent_to(minimize_dfa)

    def test_regex_concatenation(self):
        regex = Regex("a b")
        minimal_dfa = create_minimal_dfa(regex)
        assert minimal_dfa.accepts([Symbol("a"), Symbol("b")])

        minimal_dfa = create_minimal_dfa(regex.concatenate(Regex("c")))
        assert not minimal_dfa.accepts([Symbol("a"), Symbol("b")])
        assert minimal_dfa.accepts([Symbol("a"), Symbol("b"), Symbol("c")])

    def test_regex_union(self):
        regex = Regex("abc|d")
        minimal_dfa = create_minimal_dfa(regex)
        assert minimal_dfa.accepts([Symbol("abc")])
        assert not minimal_dfa.accepts([Symbol("abc"), Symbol("d")])
        assert not minimal_dfa.accepts([Symbol("a"), Symbol("b"), Symbol("c")])

    def test_regex_kleene_star(self):
        regex_kleene = Regex("a").kleene_star()
        minimal_dfa = create_minimal_dfa(regex_kleene)
        assert minimal_dfa.accepts([Symbol("a")])
        assert minimal_dfa.accepts([Symbol("a"), Symbol("a"), Symbol("a")])

    def test_create_nfa(self):
        nfa = create_nfa(load_graph("skos"))
        assert not nfa.is_deterministic()

    def test_nfa_with_expected(self):
        graph = create_labeled_two_cycle_graph(1, 1, ("a", "b"))
        nfa = create_nfa(graph, {0}, {2})

        st_0 = State(0)
        st_1 = State(1)
        st_2 = State(2)
        sym_a = Symbol("a")
        sym_b = Symbol("b")
        nfa_compare = NondeterministicFiniteAutomaton()

        nfa_compare.add_start_state(st_0)
        nfa_compare.add_final_state(st_2)
        nfa_compare.add_transitions(
            [
                (st_1, sym_a, st_0),
                (st_0, sym_a, st_1),
                (st_2, sym_b, st_0),
                (st_0, sym_b, st_2),
            ]
        )

        assert nfa.is_equivalent_to(nfa_compare)
