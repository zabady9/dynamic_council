from pydantic import BaseModel, Field
from langchain_core.messages import AIMessage
from state import DynamicState
from .llm_setup import get_pro_llm

class CollectorSchema(BaseModel):
    is_ready: bool = Field(
        description="True ONLY if the user has provided enough basic context (the core problem/goal AND some industry/background context) to write a useful report. False if critical elements are missing."
    )
    response_to_user: str = Field(
        description="CRITICAL: You MUST write this response in the EXACT SAME LANGUAGE the user used in their last message (e.g., if Arabic, reply in Arabic). If is_ready is False, write exactly ONE simple, friendly clarifying question. If True, write a brief, polite acknowledgment."
    )

def collector_node(state: DynamicState) -> dict:
    """
    The Requirement Collector Agent.
    Reviews the conversation history to determine if the brief is actionable.
    If not, it asks a follow-up question and halts the process.
    """
    llm = get_pro_llm()
    structured_llm = llm.with_structured_output(CollectorSchema)

    # Format conversation history
    convo = ""
    for m in state.get("messages", []):
        role = "CLIENT" if m.type == "human" else "INTAKE SPECIALIST"
        convo += f"{role}: {m.content}\n"

    prompt = f"""You are a helpful, easy-going Intake Assistant at a consulting firm.
Your job is to ensure you have just enough solid information before sending the request to the expert team.

CRITICAL RULE: You MUST reply to the user in the EXACT same language they used in their message. If they speak Arabic, your `response_to_user` MUST be in Arabic. If English, use English.

A sufficient brief MUST have:
1. The core problem or goal.
2. The industry or context of the project.

Do NOT be overly demanding or ask for budgets/competitors unless necessary. Keep it friendly. But DO NOT proceed if the user just says "I want to start a company" without specifying what kind of company or what they want to achieve.

CONVERSATION HISTORY:
{convo}

If the user has provided enough basic context, set is_ready to True and provide a short, friendly acknowledgment in their language.
If they are missing the core goal or industry, set is_ready to False and ask ONE simple, direct question in their language to fill the gap."""

    response = structured_llm.invoke(prompt)

    return {
        "requirements_met": response.is_ready,
        "messages": [AIMessage(content=response.response_to_user)]
    }
