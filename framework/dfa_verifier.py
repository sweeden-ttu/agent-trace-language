# ===== framework/dfa_verifier.py =====
"""A minimal deterministic finite automaton (DFA) verifier.

The verifier checks whether a projected trace belongs to a language
specified by a DFA. The DFA is defined by a set of states, a start
state, a set of accepting states, and a transition function.

For the purposes of the open‑source framework we provide a simple
implementation that can be instantiated with a transition dictionary.
More elaborate DFAs can be generated from regular expressions or
hand‑crafted specifications.
"""

from typing import Dict, Tuple, Any, List

class DFA:
    """Deterministic Finite Automaton.

    Attributes:
        states (set): All states of the automaton.
        start_state (hashable): The initial state.
        accept_states (set): Accepting/final states.
        transition (dict): Mapping (state, symbol) -> next_state.
    """
    def __init__(self, states: set, start_state: Any, accept_states: set,
                 transition: Dict[Tuple[Any, str], Any]):
        self.states = states
        self.start_state = start_state
        self.accept_states = accept_states
        self.transition = transition

    def step(self, state: Any, symbol: str) -> Any:
        """Consume a symbol and return the next state.

        Raises a ``KeyError`` if the transition is undefined, which
        indicates that the trace is rejected by the DFA.
        """
        return self.transition[(state, symbol)]

    def accepts(self, trace: List[str]) -> bool:
        """Return ``True`` if the trace is accepted by the DFA.
        """
        current = self.start_state
        try:
            for sym in trace:
                current = self.step(current, sym)
        except KeyError:
            return False
        return current in self.accept_states

# Example construction – a toy DFA that accepts the language a* b+.
def example_dfa() -> DFA:
    states = {"q0", "q1", "q_dead"}
    start = "q0"
    accept = {"q1"}
    # Transition table: (state, symbol) -> next_state
    transition = {
        ("q0", "a"): "q0",
        ("q0", "b"): "q1",
        ("q1", "b"): "q1",
        ("q1", "a"): "q_dead",
        ("q_dead", "a"): "q_dead",
        ("q_dead", "b"): "q_dead",
    }
    return DFA(states, start, accept, transition)
