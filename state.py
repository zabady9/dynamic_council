from typing import Annotated
from typing_extensions import TypedDict
import operator
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

def merge_dicts(a: dict, b: dict) -> dict:
    """Merges two dictionaries, prioritizing keys from b if there are overlaps."""
    if b.get("__CLEAR__"):
        return {}
    merged = a.copy()
    merged.update(b)
    return merged

class DynamicState(TypedDict):
    # History of the conversation
    messages: Annotated[list[AnyMessage], add_messages]
    
    # Check if we have enough info to proceed
    requirements_met: bool
    
    # Original dynamic fields
    outline: str
    active_agents: list[str]
    agent_outputs: Annotated[dict, merge_dicts]
    validated_bullets: str
    final_document: str
    
    # The rewritten, clean query
    refined_query: str
