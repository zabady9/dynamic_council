from state import DynamicState
from .llm_setup import get_pro_llm

def rewriter_node(state: DynamicState) -> dict:
    """
    The Query Rewriter Agent.
    Takes the messy back-and-forth conversation history and rewrites it into a 
    single, pristine, and comprehensive 'Master Project Brief'.
    """
    llm = get_pro_llm()
    
    convo = ""
    for m in state.get("messages", []):
        if m.type in ("human", "ai"):
            role = "CLIENT" if m.type == "human" else "INTAKE SPECIALIST"
            convo += f"{role}: {m.content}\n"
    
    prompt = f"""You are a human project coordinator taking clear, direct notes from a conversation.
Your task is to review the following conversation history between a client and an intake specialist, 
and summarize the client's actual requirements into a single, clean "Project Brief".

CONVERSATION HISTORY:
{convo}

YOUR TASK:
1. Extract ONLY the facts, requirements, constraints, and context provided by the client.
2. DO NOT overthink, hallucinate, or add details the client did not explicitly mention.
3. Keep it simple and direct. Do not write a long essay or use overly formal "consulting" fluff.
4. Structure the notes cleanly with basic headers (e.g., ## Goal, ## Industry, ## Constraints)."""

    response = llm.invoke(prompt)
    
    return {"refined_query": response.content}
