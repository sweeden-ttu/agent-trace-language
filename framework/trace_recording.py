# ===== framework/trace_recording.py =====
"""Simple trace recording utilities.

This module provides functions to record execution traces of an agent.
A trace is a list of operation symbols (strings) that represent the
steps taken by the generator. The implementation is lightweight and
suitable for inclusion in the open‑source framework accompanying the
paper.
"""

from typing import List

def start_trace() -> List[str]:
    """Initialize a new empty trace.

    Returns:
        A mutable list that will hold the trace symbols.
    """
    return []

def record_step(trace: List[str], symbol: str) -> None:
    """Append a single operation symbol to the trace.

    Args:
        trace: The trace list to modify.
        symbol: The operation symbol (e.g., ``load_kaggle_csvs``).
    """
    trace.append(symbol)

def finish_trace(trace: List[str]) -> List[str]:
    """Finalize and return the completed trace.

    Currently this is a no‑op placeholder that simply returns the list.
    Future extensions could include validation or serialization.
    """
    return trace
