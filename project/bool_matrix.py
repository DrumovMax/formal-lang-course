from pyformlang.finite_automaton import *
from scipy import sparse
from scipy.sparse import block_diag, csr_matrix, vstack, csr_array, lil_array


class BoolMatrix:
    """
    A class representing the NFA as a Boolean matrix
    """

    def __init__(self, nfa: NondeterministicFiniteAutomaton = None):
        if nfa is not None:
            self.states = nfa.states
            self.start_states = nfa.start_states
            self.final_states = nfa.final_states
            self.states_amount = len(self.states)
            self.states_dict = dict(
                [(state, index) for (index, state) in enumerate(nfa.states)]
            )
            self.bool_matrix = self.init_bool_matrix(nfa)
        else:
            self.states = set()
            self.start_states = set()
            self.final_states = set()
            self.states_amount = 0
            self.states_dict = {}
            self.bool_matrix = {}

    def init_bool_matrix(self, nfa: NondeterministicFiniteAutomaton):
        """
        Creation of Boolean matrices by nfa.

        Parameters
        ----------
        nfa: NondeterministicFiniteAutomaton
        Nfa by which boolean matrices will be built.
        """
        bool_decompose = {}
        shape = (self.states_amount, self.states_amount)

        for first_state, transition in nfa.to_dict().items():
            for symbol, second_states in transition.items():
                second_states = (
                    {second_states}
                    if not isinstance(second_states, set)
                    else second_states
                )

                for state in second_states:
                    first_index, second_index = (
                        self.states_dict[first_state],
                        self.states_dict[state],
                    )

                    if symbol not in bool_decompose:
                        bool_decompose[symbol] = sparse.csr_matrix(shape, dtype=bool)

                    bool_decompose[symbol][first_index, second_index] = True

        return bool_decompose

    def to_automaton(self):
        """
        Conversion of nfa to Boolean matrices.
        """
        nfa = NondeterministicFiniteAutomaton()

        for symbol, bool_matrix in self.bool_matrix.items():
            nonzero_rows, nonzero_cols = bool_matrix.nonzero()
            for i in range(len(nonzero_rows)):
                nfa.add_transition(
                    State(nonzero_rows[i]), Symbol(symbol), State(nonzero_cols[i])
                )

        for state in self.start_states:
            nfa.add_start_state(State(state))

        for state in self.final_states:
            nfa.add_final_state(State(state))

        return nfa

    def intersect(self, other):
        """
        Intersects two matrices.

        Parameters
        ----------
        other : BoolMatrix
        Returns
        -------
        intersection : BoolMatrix
            Returns the result intersection.
        """
        intersection = BoolMatrix()
        intersection.states_amount = self.states_amount * other.states_amount
        symbols = set(self.bool_matrix.keys()) & set(other.bool_matrix.keys())

        intersection.bool_matrix = {
            symbol: sparse.kron(
                self.bool_matrix[symbol], other.bool_matrix[symbol], format="csr"
            )
            for symbol in symbols
        }

        def intersect_states(first_state, second_state, first_index, second_index):
            state = first_index * other.states_amount + second_index
            return (
                state,
                state
                if first_state in self.start_states
                and second_state in other.start_states
                else None,
                state
                if first_state in self.final_states
                and second_state in other.final_states
                else None,
            )

        for first_state, first_index in self.states_dict.items():
            for second_state, second_index in other.states_dict.items():
                state_index, start_state, final_state = intersect_states(
                    first_state, second_state, first_index, second_index
                )

                if state_index is not None:
                    intersection.states_dict[state_index] = state_index
                if start_state is not None:
                    intersection.start_states.add(start_state)
                if final_state is not None:
                    intersection.final_states.add(final_state)

        return intersection

    def transitive_closure(self):
        """
        Constructs the transitive closure of an automaton.

        Returns
        -------
        adjacency_matrix : csr_matrix
            Returns transitive closure matrix
        """
        if len(self.bool_matrix) == 0:
            return sparse.csr_matrix((0, 0), dtype=bool)
        adjacency_matrix = sum(self.bool_matrix.values())

        prev = adjacency_matrix.nnz
        curr = 0

        while prev != curr:
            adjacency_matrix += adjacency_matrix @ adjacency_matrix
            prev = curr
            curr = adjacency_matrix.nnz

        return adjacency_matrix

    def direct_sum(self, other):
        matrix = {}
        symbols = set(self.bool_matrix.keys()) & set(other.bool_matrix.keys())

        for symbol in symbols:
            matrix[symbol] = block_diag(
                (other.bool_matrix[symbol], self.bool_matrix[symbol]),
                format="csr",
            )

        return matrix

    def make_front(self, other):
        front = sparse.lil_matrix(
            (other.states_amount, self.states_amount + other.states_amount)
        )

        self_start_row = sparse.lil_array(
            [[state in self.start_states for state in self.states]]
        )

        for _, i in other.states_dict.items():
            front[i, i] = True
            front[i, other.states_amount :] = self_start_row

        return front.tocsr()

    def make_separate_front(self, other):
        start_indexes = {
            index
            for index, state in enumerate(self.states)
            if state in self.start_states
        }

        fronts = [self.make_front(other) for _ in start_indexes]

        return (
            csr_matrix(vstack(fronts))
            if len(fronts) > 0
            else csr_matrix(
                other.states_amount, other.states_amount + self.states_amount
            )
        )

    def constraint_bfs(self, other, is_separate: bool = False):
        direct_sum = self.direct_sum(other)
        n = self.states_amount
        k = other.states_amount
        symbols = set(self.bool_matrix.keys()) & set(other.bool_matrix.keys())

        start_states_indices, final_states_indices, other_final_states_indices = [
            [i for i, st in enumerate(states) if st in target_states]
            for states, target_states in [
                (self.states, self.start_states),
                (self.states, self.final_states),
                (other.states, other.final_states),
            ]
        ]

        front = (
            self.make_front(other)
            if not is_separate
            else self.make_separate_front(other)
        )

        is_visited = csr_array(front.shape)

        while True:
            old_is_visited = is_visited.copy()

            for symbol in symbols:
                result = is_visited @ direct_sum[symbol]
                transform = transform_front(result, other.states_amount)
                is_visited += transform

            if old_is_visited == is_visited.nnz:
                break

        result = set()
        rows, cols = is_visited.nonzero()
        for i, j in zip(rows, cols):
            if j >= k and i % k in other_final_states_indices:
                if j - k in final_states_indices:
                    result.add(j - k) if not is_separate else result.add(
                        (start_states_indices[i // n], j - k)
                    )

        return result


def transform_front(front, amount):
    new_front = lil_array(front.shape)

    rows, cols = front.nonzero()
    for i, j in zip(rows, cols):
        if j < amount:
            row = front.getrow(i)

            if row.nnz > 1:
                new_front[[i // amount * amount + j], :] += row.tolil()

    return new_front.tocsr()
