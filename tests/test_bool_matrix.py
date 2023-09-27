from project.bool_matrix import BoolMatrix
from pyformlang.finite_automaton import *


class TestsForBoolMatrix:
    def test_empty_nfa(self):
        nfa = NondeterministicFiniteAutomaton()
        decompose = BoolMatrix(nfa)
        assert decompose.states_amount == 0
        assert not decompose.start_states
        assert not decompose.states
        assert not decompose.final_states
        assert not decompose.states_dict
        assert not decompose.bool_matrix

    def test_non_empty_nfa(self):
        nfa = NondeterministicFiniteAutomaton()
        state0 = State(0)
        state1 = State(1)
        state2 = State(2)
        state3 = State(3)
        state4 = State(4)

        symb_a = Symbol("a")
        symb_b = Symbol("b")
        symb_c = Symbol("c")
        symb_d = Symbol("d")

        nfa.add_start_state(state0)

        nfa.add_final_state(state4)
        nfa.add_final_state(state3)

        nfa.add_transition(state0, symb_a, state1)
        nfa.add_transition(state1, symb_b, state1)
        nfa.add_transition(state1, symb_c, state2)
        nfa.add_transition(state1, symb_d, state3)
        nfa.add_transition(state1, symb_c, state4)
        nfa.add_transition(state1, symb_b, state4)

        decompose = BoolMatrix(nfa)
        assert decompose.states_amount == 5
        assert decompose.start_states == {0}
        assert decompose.final_states == {3, 4}
        assert decompose.states_dict == {2: 2, 1: 1, 4: 4, 3: 3, 0: 0}

    def test_intersect(self):
        nfa1 = NondeterministicFiniteAutomaton()

        state0 = State(0)
        state1 = State(1)
        state2 = State(2)
        state3 = State(3)
        state4 = State(4)
        state5 = State(5)
        state7 = State(7)
        state8 = State(8)

        symb_a = Symbol("a")
        symb_b = Symbol("b")
        symb_c = Symbol("c")

        nfa1.add_start_state(state0)
        nfa1.add_final_state(state1)
        nfa1.add_transition(state0, symb_c, state0)
        nfa1.add_transition(state1, symb_a, state1)
        nfa1.add_transition(state1, symb_c, state1)
        nfa1.add_transition(state1, symb_b, state2)
        nfa1.add_transition(state2, symb_b, state1)
        boolean_nfa1 = BoolMatrix(nfa1)

        nfa2 = NondeterministicFiniteAutomaton()
        nfa2.add_start_state(state0)
        nfa2.add_final_state(state2)
        nfa2.add_transition(state0, symb_a, state1)
        nfa2.add_transition(state1, symb_b, state2)
        nfa2.add_transition(state2, symb_c, state2)
        boolean_nfa2 = BoolMatrix(nfa2)

        actual_intersection = BoolMatrix.intersect(boolean_nfa1, boolean_nfa2)

        expected_nfa = NondeterministicFiniteAutomaton()
        expected_nfa.add_start_state(state0)
        expected_nfa.add_final_state(state5)
        expected_nfa.add_transition(state4, symb_b, state8)
        expected_nfa.add_transition(state7, symb_b, state5)
        expected_nfa.add_transition(state3, symb_a, state4)
        expected_nfa.add_transition(state2, symb_c, state2)
        expected_nfa.add_transition(state5, symb_c, state5)

        expected_intersection = BoolMatrix(expected_nfa)

        assert actual_intersection.states_amount == len(nfa1.states) * len(nfa2.states)
        assert actual_intersection.start_states == expected_intersection.start_states
        assert actual_intersection.final_states == expected_intersection.final_states

    def test_for_transitive_closure(self):
        nfa = NondeterministicFiniteAutomaton()
        nfa.add_transitions(
            [
                (0, "C", 1),
                (1, "L", 2),
                (2, "O", 3),
                (3, "S", 4),
                (4, "U", 5),
                (5, "R", 6),
                (6, "E", 7),
            ]
        )
        bool_matrix = BoolMatrix(nfa)
        transitive_closure = bool_matrix.transitive_closure()
        assert transitive_closure.sum() == transitive_closure.size
