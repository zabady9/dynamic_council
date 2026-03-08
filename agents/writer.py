from state import DynamicState
from .llm_setup import get_flash_llm

def writer_node(state: DynamicState) -> dict:
    """
    The Master Writer. Takes the strict outline and the validated bullet points
    from the War Room and produces the polished final prose.
    """
    llm = get_flash_llm()

    prompt = f"""You are the Master Writer at a top consulting firm.
Your team has already done the research and resolved all logical contradictions.
Your ONLY job is to turn their verified bullet points into a polished, executive-ready document.

MASTER OUTLINE (Follow this structure exactly):
{state['outline']}

VERIFIED BULLET POINTS (The facts you must use):
{state['validated_bullets']}

INSTRUCTIONS:
1. Write the final document.
2. CRITICAL - COHESION: The document MUST read as a single, seamless, and compelling narrative. Use smooth transitions between sections. It should NOT read like separate reports stitched together.
3. CRITICAL - SCENARIO INTEGRATION: Weave the 'Case Study' or 'Client Scenario' naturally into the executive summary and throughout the relevant sections to anchor the strategy and make it highly impactful for decision-makers.
4. DEPTH: Ensure all sections (especially UX, Tech, and Finance) have substantial depth based on the provided bullets. Do not summarize too broadly.
5. Maintain an executive, clear, and professional tone.
6. Do not invent new facts or data. Rely strictly on the verified bullet points.
7. Format cleanly with markdown headers, bold text for emphasis, and paragraphs where appropriate.

Output the full, final, cohesive document."""

    response = llm.invoke(prompt)

    return {"final_document": response.content}
