from graph.state import State

def final_report_builder(state: State) -> dict:
    """
    Build a structured final report.
    IMPORTANT: return PARTIAL STATE only.
    """

    lines = []

    # =========================
    # 1. SUMMARY
    # =========================
    lines.append("## 📌 Summary")

    if state["scope"] == "function":
        lines.append(
            f"- **What the file does:** Contains logic related to the function `{state['function_name']}`."
        )
    else:
        lines.append(
            "- **What the file does:** Implements application logic and utility functions."
        )

    score = state.get("score")
    lines.append(f"- **Code Quality Score:** {score if score is not None else 'N/A'} / 10")

    if state["risks"]:
        high_risks = [r for r in state["risks"] if r["severity"] == "high"]
        if high_risks:
            lines.append(
                f"- **Notable issues:** {len(high_risks)} high-severity issue(s) detected."
            )
        else:
            lines.append("- **Notable issues:** No high-severity issues detected.")
    else:
        lines.append("- **Notable issues:** No issues detected.")

    if not state["risks"]:
        lines.append("- **Strong points:** Code is clean and free of detected issues.")
    else:
        lines.append(
            "- **Strong points:** Clear structure and readable logic, but requires improvements."
        )

    lines.append("")

    # =========================
    # 2. RISKS
    # =========================
    lines.append("## ⚠️ Risks")

    if not state["risks"]:
        lines.append("- No risks found.")
    else:
        for i, risk in enumerate(state["risks"], start=1):
            lines.append(f"{i}. **{risk['description']}**")
            lines.append(f"   - Severity: {risk['severity']}")
            lines.append(f"   - Description: {risk['reason']}")
            lines.append(f"   - Line reference(s): `{risk['faulty_code']}`")

    lines.append("")

    # =========================
    # 3. SUGGESTED FIXES
    # =========================
    lines.append("## ✅ Suggested Fixes")

    if not state["suggestions"]:
        lines.append("- No suggested fixes available.")
    else:
        for i, s in enumerate(state["suggestions"], start=1):
            lines.append(f"{i}. **{s['description']}**")
            lines.append(f"   - Fix: {s['fix']}")

    # ✅ THIS IS CRITICAL
    return {
        "final_report": "\n".join(lines)
    }
