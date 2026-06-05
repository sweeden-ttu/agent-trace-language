# ===== framework/language_analysis.py =====
"""Language analysis utilities for the trace‑language framework.

These helpers provide simple statistics over traces such as
distribution of symbols, trace length histogram, and success/invalid
rates for a given verifier.
"""

from collections import Counter
from typing import List, Tuple

def symbol_frequencies(trace: List[str]) -> Counter:
    """Return a Counter of symbol occurrences in the trace."""
    return Counter(trace)

def trace_lengths(traces: List[List[str]]) -> List[int]:
    """Return a list of lengths for each trace in a collection."""
    return [len(t) for t in traces]

def success_rate(traces: List[List[str]], verifier) -> Tuple[float, float]:
    """Compute success and invalid rates given a verifier.

    Args:
        traces: List of raw generator traces.
        verifier: An object with an ``accepts`` method (e.g., DFA).
    Returns:
        (success_rate, invalid_rate) where success_rate is the fraction of
        traces accepted by the verifier and invalid_rate is the fraction
        rejected (or invalid for generator‑only case).
    """
    total = len(traces)
    if total == 0:
        return 0.0, 0.0
    accepted = sum(1 for t in traces if verifier.accepts(t))
    success = accepted / total
    invalid = 1.0 - success
    return success, invalid
