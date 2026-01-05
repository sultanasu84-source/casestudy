import json
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



suggestion_prompt = PromptTemplate(
    input_variables=["risks"],
    template="""
You are a senior engineer.
Suggest fixes.

FORMAT:
{{
  "suggestions": [
    {{
      "description": "string",
      "fix": "string"
    }}
  ]
}}

Risks:
{risks}
"""
)



def suggestion_generator(state: State) -> dict:
    """
    Generate code fix suggestions from detected risks.
    IMPORTANT: return PARTIAL STATE only.
    """

    # No risks → no suggestions
    if not state["risks"]:
        return {
            "suggestions": []
        }

    prompt_text = suggestion_prompt.format_prompt(
        risks=json.dumps(state["risks"], indent=2)
    ).to_string()

    response = llm.invoke(prompt_text)
    cleaned = clean_json(response.content)

    try:
        suggestions = json.loads(cleaned).get("suggestions", [])
    except json.JSONDecodeError:
        print("\n❌ Invalid JSON from LLM (suggestions):")
        print(cleaned)
        suggestions = []

    return {
        "suggestions": suggestions
    }
