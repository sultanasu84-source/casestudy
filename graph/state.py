from typing import TypedDict, List, Optional, Dict, Any
from typing import Annotated
from operator import add

class State(TypedDict):
    user_message: str
    code_text: str

    scope: str
    aspects: List[str]
    function_name: Optional[str]
    request: Dict[str, Any]

    code_to_analyze: str
    is_valid: bool
    validation_error: Optional[str]

    risks: Annotated[list, add]
    suggestions: List[Dict[str, Any]]

    score: int
    final_report: str
