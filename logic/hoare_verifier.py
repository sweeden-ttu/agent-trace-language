# logic/hoare_verifier.py
"""Minimal Hoare‑logic verifier for a trace‑language step.
The verifier checks a simple pre‑condition/post‑condition triple for a given
function call. This is *illustrative* only; it does not attempt full program
verification.
"""

def hoare_verify(pre, action, post):
    """Return True if the action respects the Hoare triple.

    Args:
        pre (callable): A predicate on the input state.
        action (callable): The operation to execute.
        post (callable): A predicate on the output state.
    """
    # Simple mock: we assume the state is a dict.
    state = {}
    if not pre(state):
        return False
    new_state = action(state)
    return post(new_state)

# Example usage (in documentation snippets)
if __name__ == "__main__":
    pre = lambda s: s.get("counter", 0) >= 0
    action = lambda s: {**s, "counter": s.get("counter", 0) + 1}
    post = lambda s: s["counter"] == 1
    print("Hoare triple holds:" , hoare_verify(pre, action, post))
