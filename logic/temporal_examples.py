# logic/temporal_examples.py
"""Tiny LTL/CTL examples used in the methodology section.
These functions illustrate how a temporal property could be checked over a
sequence of trace‑language actions. They are *illustrative* and not meant to be
full‑featured model checkers.
"""
from typing import List

def ltl_always(predicate, trace: List[dict]) -> bool:
    """Return True if *predicate* holds for every state in *trace*.

    Args:
        predicate: Callable taking a state dict and returning bool.
        trace: List of state dictionaries representing the execution trace.
    """
    return all(predicate(state) for state in trace)

def ctl_exists_next(predicate, trace: List[dict]) -> bool:
    """Return True if there exists a *next* state in the trace satisfying *predicate*.
    This mimics the CTL *EX* operator.
    """
    for i in range(len(trace) - 1):
        if predicate(trace[i + 1]):
            return True
    return False

# Example usage (will be referenced in the paper)
if __name__ == "__main__":
    # Simple trace of counters
    trace = [{"counter": i} for i in range(5)]
    always_non_negative = ltl_always(lambda s: s["counter"] >= 0, trace)
    exists_next_three = ctl_exists_next(lambda s: s["counter"] == 3, trace)
    print("LTL always non‑negative:", always_non_negative)
    print("CTL EX counter == 3 exists:", exists_next_three)
