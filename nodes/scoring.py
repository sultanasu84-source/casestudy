from graph.state import State


def scoring_node(state: State) -> dict:
    """
    Calculate code quality score based on risks severity.
    IMPORTANT: return PARTIAL STATE only.
    """
    score = 10

    for risk in state["risks"]:
        severity = risk.get("severity", "").lower()

        if severity == "high":
            score -= 3
        elif severity == "medium":
            score -= 2
        elif severity == "low":
            score -= 1

    return {
        "score": max(score, 0)
    }
