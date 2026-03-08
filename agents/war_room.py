from state import DynamicState
from .llm_setup import get_pro_llm

def war_room_node(state: DynamicState) -> dict:
    """
    The War Room. All activated experts have finished their bullet points.
    This node checks for contradictions, aligns the data, and organizes it according to the Master Outline.
    """
    llm = get_pro_llm()
    
    outputs = state.get("agent_outputs", {})
    if not outputs:
        combined_bullets = "No expert data gathered."
    else:
        # Combine all dictionary values into a single string for the LLM to read
        combined_bullets = "\n\n".join([f"=== {agent_name.upper()} DATA ===\n{bullets}" for agent_name, bullets in outputs.items()])

    prompt = f"""You are the Strategy Director presiding over the "War Room".
Your experts have just returned with their raw bullet points. 

MASTER OUTLINE:
{state['outline']}

EXPERT DATA:
{combined_bullets}

YOUR TASK:
1. Synthesize all this raw data.
2. Resolve any contradictions (e.g., if Marketing assumes a $1M budget but Finance says $100k, align them logically).
3. Organize the synthesized bullet points directly under the relevant headers from the MASTER OUTLINE.
4. CRITICAL: Ensure the 'Case Study' or 'Client Scenario' provided by the experts is deeply integrated and that the entire set of bullet points flows logically as a single, cohesive narrative.
5. Maintain a bullet-point format. Do not write prose yet. Your output is the verified, seamlessly integrated blueprint for the Writer.

Output ONLY the validated and organized bullet points."""

    response = llm.invoke(prompt)

    return {"validated_bullets": response.content}
