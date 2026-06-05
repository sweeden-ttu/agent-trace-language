# ===== framework/projection.py =====
"""Projection utilities for mapping generator traces to verifier language.

The projection step transforms a raw generator trace (a sequence of symbols)
into the representation required by the DFA verifier. In the current
prototype the projection is a simple identity mapping, but the module
provides a place for more sophisticated transformations such as token
normalisation, abstraction, or embedding of contextual information.
"""

def project_trace(trace):
    """Project a generator trace onto the verifier alphabet.

    Args:
        trace (list of str): The original trace produced by the generator.
    Returns:
        list of str: The projected trace suitable for DFA verification.
    """
    # Placeholder: identity projection. Extend as needed.
    return list(trace)
