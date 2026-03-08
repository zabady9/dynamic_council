from langchain_community.tools import DuckDuckGoSearchResults
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from state import DynamicState
from .llm_setup import get_flash_llm

search_tool = DuckDuckGoSearchResults(max_results=3)

def make_expert_node(name: str, domain: str):
    """
    Factory function to generate specific expert nodes dynamically.
    Each expert uses a ReAct loop with DuckDuckGo to gather data and returns bullet points.
    """
    def expert_node(state: DynamicState) -> dict:
        llm = get_flash_llm()
        
        system_prompt = f"""You are the {name}.
Your Domain of Expertise: {domain}.

Your task is to conduct research and provide highly specific, data-driven BULLET POINTS for your domain.
CRITICAL INSTRUCTION: Your output MUST be hyper-tailored to the specific industry and goal. 
- Avoid generic market sizes or vague CAGR numbers. Provide actionable, specific metrics.
- Dive DEEP into technical, strategic, or user experience (UX/CX) details. Do not be superficial.
- MANDATORY CASE STUDY: If your domain relates to the 'Case Study' or 'Scenario' section of the outline, find and summarize a real-world case study or construct a highly realistic scenario with hard numbers to anchor the strategy.
- MANDATORY COMPETITOR ANALYSIS: If your domain covers business, finance, or strategy, you MUST research specific direct competitors. You MUST provide bullet points for a Comparative SWOT Analysis, Pricing Comparisons, and define a clear Competitive Advantage.

MASTER PROJECT BRIEF:
{state.get('refined_query', '')}

MASTER OUTLINE (so you know where your work fits):
{state['outline']}

INSTRUCTIONS:
1. Search the web for real, specific data, tools, case studies, competitor info, and facts relevant to your domain and this specific brief.
2. DO NOT write paragraphs or prose.
3. ONLY output dense, factual bullet points directly answering the needs of the Master Outline.
4. Focus strictly on your domain. Do not overlap with other experts.
"""
        # Create a ReAct agent equipped with search
        agent = create_react_agent(llm, tools=[search_tool], prompt=system_prompt)
        
        # Execute the agent
        result = agent.invoke({
            "messages": [HumanMessage(content="Begin your research and output the final bullet points.")]
        })
        
        final_bullets = result["messages"][-1].content
        
        # Return a dictionary mapped by agent name. LangGraph's merge_dicts will combine them.
        return {"agent_outputs": {name: final_bullets}}

    return expert_node

# Instantiate the specialized agents
business_expert = make_expert_node("business_expert", "Market sizing, competitor analysis, business strategy")
tech_expert = make_expert_node("tech_expert", "Cloud infrastructure, software architecture, technical feasibility")
finance_expert = make_expert_node("finance_expert", "Financial modeling, cost projections, ROI, pricing")
brand_expert = make_expert_node("brand_expert", "Brand positioning, value proposition, identity")
marketing_expert = make_expert_node("marketing_expert", "Go-to-market channels, campaigns, KPIs")
