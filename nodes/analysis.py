import json
from typing import List, Dict, Any
from langchain_core.prompts import PromptTemplate
from graph.state import State
from llm import llm

def clean_json(text) -> str:
    if text is None:
        raise ValueError("clean_json received None")

    if not isinstance(text, str):
        text = str(text)

    text = text.strip()

    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 2:
            text = parts[1].strip()

    if text.lower().startswith("json"):
        text = text[4:].strip()

    if not text:
        raise ValueError("clean_json produced empty string")

    return text


# ======================================================
# LLM
# ======================================================

def analyze_single_aspect(
    *,
    code: str,
    aspect: str,
    scope: str,
    function_name: str | None
) -> List[Dict[str, Any]]:

    prompt_text = DYNAMIC_ASPECT_PROMPT.format_prompt(
        code=code,
        aspect=aspect,
        scope=scope,
        function_name=function_name or "N/A"
    ).to_string()

    response = llm.invoke(prompt_text)
    cleaned = clean_json(response.content)

    try:
        return json.loads(cleaned).get("risks", [])
    except json.JSONDecodeError:
        print(f"\n❌ Invalid JSON for aspect: {aspect}")
        print(cleaned)
        return []

# ======================================================
# Analysis Router (CONDITIONAL EDGE)
# ======================================================
def analysis_router(state: State) -> str:
    """
    Decide which analysis path to take based on scope & aspects.
    """
    is_general = len(state["aspects"]) == 1 and state["aspects"][0] == "general"

    if state["scope"] == "full" and is_general:
        return "full_general"

    if state["scope"] == "full":
        return "full_aspect"

    if state["scope"] == "function" and is_general:
        return "function_general"

    return "function_aspect"


# ======================================================
# Risk JSON format

RISK_FORMAT = """
FORMAT:
{{
  "risks": [
    {{
      "description": "string",
      "severity": "low | medium | high",
      "reason": "string",
      "faulty_code": "string"
    }}
  ]
}}
"""

# ======================================================
# Prompts
# ======================================================
full_general_prompt = PromptTemplate(
    input_variables=["code"],
    template="""
You are a senior software engineer.
Perform a GENERAL code review.
""" + RISK_FORMAT + """

Code:
{code}
"""
)

function_general_prompt = PromptTemplate(
    input_variables=["code", "function_name"],
    template="""
Review FUNCTION {function_name} with GENERAL focus.
""" + RISK_FORMAT + """

Function Code:
{code}
"""
)
DYNAMIC_ASPECT_PROMPT = PromptTemplate(
    input_variables=["code", "aspect", "scope", "function_name"],
    template="""
You are a specialist code reviewer.

Review the following code.

Scope: {scope}
Function: {function_name}

🎯 Focus STRICTLY AND EXCLUSIVELY on the following aspect:
👉 {aspect}

Rules:
- Identify ONLY issues related to "{aspect}"
- Ignore all other concerns completely
- If no issues exist for "{aspect}", return an empty list
- Do NOT mention any other aspects

Return VALID JSON ONLY.

FORMAT:
{{
  "risks": [
    {{
      "aspect": "{aspect}",
      "description": "string",
      "severity": "low | medium | high",
      "reason": "string",
      "faulty_code": "string"
    }}
  ]
}}

Code:
{code}
"""
)



# ======================================================
# Analysis Runner (shared helper)
# ======================================================
def run_analysis(
    prompt: PromptTemplate,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Runs LLM analysis and safely parses JSON risks.
    """
    prompt_text = prompt.format_prompt(**kwargs).to_string()
    response = llm.invoke(prompt_text)

    cleaned = clean_json(response.content)

    try:
        return json.loads(cleaned).get("risks", [])
    except json.JSONDecodeError:
        print("\n❌ Invalid JSON from LLM:")
        print(cleaned)
        return []


# ======================================================
# Analysis Nodes (IMPORTANT: return PARTIAL STATE ONLY)
# ======================================================
def full_general_analysis(state: State) -> dict:
    return {
        "risks": run_analysis(
            full_general_prompt,
            code=state["code_to_analyze"]
        )
    }


def function_general_analysis(state: State) -> dict:
    return {
        "risks": run_analysis(
            function_general_prompt,
            code=state["code_to_analyze"],
            function_name=state["function_name"]
        )
    }

def full_aspect_analysis(state: State) -> dict:
    all_risks = []

    for aspect in state["aspects"]:
        risks = analyze_single_aspect(
            code=state["code_to_analyze"],
            aspect=aspect,
            scope="full",
            function_name=None
        )
        all_risks.extend(risks)

    return {"risks": all_risks}
def function_aspect_analysis(state: State) -> dict:
    all_risks = []

    for aspect in state["aspects"]:
        risks = analyze_single_aspect(
            code=state["code_to_analyze"],
            aspect=aspect,
            scope="function",
            function_name=state["function_name"]
        )
        all_risks.extend(risks)

    return {"risks": all_risks}
