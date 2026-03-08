from pydantic import BaseModel, Field
from state import DynamicState
from .llm_setup import get_pro_llm

class SupervisorSchema(BaseModel):
    outline: str = Field(description="A strict, detailed Table of Contents for the final deliverable. MUST be highly customized to the client's industry and problem. CRITICAL: You MUST include a dedicated section for a 'Real-World Case Study' or 'Specific Client Scenario'. CRITICAL 2: You MUST include a 'Detailed Competitor Analysis' section that specifically covers: Direct Competitors, Comparative SWOT analysis, Pricing comparison, and Competitive Advantage/Differentiation. The outline must flow as a single cohesive narrative.")
    active_agents: list[str] = Field(
        description="List of exact agent names to activate. Options: 'business_expert', 'tech_expert', 'finance_expert', 'brand_expert', 'marketing_expert'. ONLY pick the ones explicitly necessary for this brief."
    )

def supervisor_node(state: DynamicState) -> dict:
    """
    The Engagement Manager. Analyzes the refined brief, creates the master outline,
    and dynamically selects which expert agents to wake up.
    """
    llm = get_pro_llm()
    structured_llm = llm.with_structured_output(SupervisorSchema)

    prompt = f"""You are the Engagement Manager at an elite consulting firm.
A client has provided the following requirements (Master Project Brief):
\"\"\"
{state.get('refined_query', '')}
\"\"\"

Your job:
1. Determine the EXACT structure of the final document (Outline). The outline MUST be deeply tailored to the client's industry. Do not use generic consulting templates. 
   - Example: For a software house asking for AI solutions, include specific use-cases, metrics, and a cohesive flow.
   - MANDATORY 1: Include a section dedicated to a specific Case Study or highly realistic User/Client Scenario.
   - MANDATORY 2: Include a 'Competitor Analysis' section that MUST contain subsections for: 1) Direct Competitors (e.g., other software houses offering similar AI solutions), 2) Comparative SWOT Analysis, 3) Pricing Comparison, and 4) Competitive Advantage.
2. Select the MINIMUM necessary team of experts to research and populate this outline. 

Available Experts:
- business_expert: Market sizing, competitor analysis, business strategy
- tech_expert: Cloud infrastructure, software architecture, technical feasibility
- finance_expert: Financial modeling, cost projections, ROI, pricing
- brand_expert: Positioning, value proposition, identity
- marketing_expert: Go-to-market channels, campaigns, KPIs

Return the strict outline and the list of chosen agents."""

    response = structured_llm.invoke(prompt)

    # Fallback to ensure we have at least one agent if the LLM picks zero
    agents = response.active_agents if response.active_agents else ["business_expert"]

    return {
        "outline": response.outline,
        "active_agents": agents,
        "agent_outputs": {"__CLEAR__": True} # Clear previous expert data
    }
