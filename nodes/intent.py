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



intent_prompt = PromptTemplate(
    input_variables=["user_message"],
    template="""
You are an intent extraction engine for a code review assistant.

Return VALID JSON ONLY.

FORMAT:
{{
  "scope": "full | function",
  "aspects": ["general | security | performance | readability"],
  "function_name": "string | null",
  "request": {{}}
}}

User message:
{user_message}
"""
)


def intent_node(state: State) -> dict:
    prompt_text = intent_prompt.format_prompt(
        user_message=state["user_message"]
    ).to_string()

    response = llm.invoke(prompt_text)

    if response is None:
        raise ValueError("LLM returned None")

    if not hasattr(response, "content"):
        raise ValueError(f"LLM response has no content: {response}")

    cleaned = clean_json(response.content)

    data = json.loads(cleaned)

    return {
        "scope": data["scope"],
        "aspects": data["aspects"],
        "function_name": data["function_name"],
        "request": data.get("request", {})
    }
