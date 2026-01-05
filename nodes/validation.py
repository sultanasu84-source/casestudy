import ast
from typing import Optional
from graph.state import State


def extract_function(code: str, name: str) -> Optional[str]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            lines = code.splitlines()
            return "\n".join(lines[node.lineno - 1 : node.end_lineno])

    return None


def validation_node(state: State) -> dict:
    """
    Validate user intent and prepare code for analysis.
    IMPORTANT: return PARTIAL STATE only.
    """

    # =========================
    # 1️⃣ Validate aspects
    # =========================
    if not state["aspects"]:
        return {
            "is_valid": False,
            "validation_error": "No analysis aspects provided."
        }

    # =========================
    # 2️⃣ Validate scope
    # =========================
    if state["scope"] not in ("full", "function"):
        return {
            "is_valid": False,
            "validation_error": f"Invalid scope: {state['scope']}"
        }

    # =========================
    # 3️⃣ Default: full code
    # =========================
    code_to_analyze = state["code_text"]

    # =========================
    # 4️⃣ Function-level logic
    # =========================
    if state["scope"] == "function":

        if state["function_name"] is None:
            return {
                "is_valid": False,
                "validation_error": (
                    "Function-level review requested without function name."
                )
            }

        extracted = extract_function(
            state["code_text"],
            state["function_name"]
        )

        if not extracted:
            return {
                "is_valid": False,
                "validation_error": (
                    f"Function '{state['function_name']}' was not found in the code."
                )
            }

        code_to_analyze = extracted

    # =========================
    # ✅ Validation passed
    # =========================
    return {
        "is_valid": True,
        "validation_error": None,
        "code_to_analyze": code_to_analyze
    }
