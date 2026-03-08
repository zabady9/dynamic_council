from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from state import DynamicState
from agents import (
    collector_node,
    supervisor_node,
    business_expert,
    tech_expert,
    finance_expert,
    brand_expert,
    marketing_expert,
    war_room_node,
    writer_node,
    rewriter_node,
)

def route_after_collector(state: DynamicState):
    """
    If the collector has gathered enough requirements, move to the rewriter to refine them.
    Otherwise, pause the graph (END) to wait for the user's response.
    """
    if state.get("requirements_met"):
        return "rewriter"
    return END

def route_to_experts(state: DynamicState):
    """
    Reads the active_agents list created by the supervisor and returns it.
    LangGraph will automatically route to every node name in this list in parallel.
    """
    agents = state.get("active_agents", [])
    valid_agents = {"business_expert", "tech_expert", "finance_expert", "brand_expert", "marketing_expert"}
    
    # Filter to ensure we only return valid node names
    chosen = [a for a in agents if a in valid_agents]
    if not chosen:
        return ["business_expert"] # Safe fallback
    return chosen

def build_dynamic_graph(memory=None) -> StateGraph:
    """
    Builds the Dynamic Supervisor graph with conversational history support.
    """
    builder = StateGraph(DynamicState)

    # ── ADD NODES ─────────────────────────────────────────────────────────────
    builder.add_node("collector", collector_node)
    builder.add_node("rewriter", rewriter_node)
    builder.add_node("supervisor", supervisor_node)
    
    builder.add_node("business_expert", business_expert)
    builder.add_node("tech_expert", tech_expert)
    builder.add_node("finance_expert", finance_expert)
    builder.add_node("brand_expert", brand_expert)
    builder.add_node("marketing_expert", marketing_expert)
    
    builder.add_node("war_room", war_room_node)
    builder.add_node("writer", writer_node)

    # ── ADD EDGES ─────────────────────────────────────────────────────────────
    
    # 1. Start -> Collector
    builder.add_edge(START, "collector")

    # 2. Collector -> Conditional (Rewriter or Wait for User)
    builder.add_conditional_edges("collector", route_after_collector, {"rewriter": "rewriter", END: END})

    # 3. Rewriter -> Supervisor
    builder.add_edge("rewriter", "supervisor")

    # 4. Supervisor -> Experts (Dynamic Fan-Out)
    builder.add_conditional_edges(
        "supervisor",
        route_to_experts,
        {
            "business_expert": "business_expert",
            "tech_expert": "tech_expert",
            "finance_expert": "finance_expert",
            "brand_expert": "brand_expert",
            "marketing_expert": "marketing_expert",
        }
    )

    # 5. Experts -> War Room (Fan-In)
    builder.add_edge("business_expert", "war_room")
    builder.add_edge("tech_expert", "war_room")
    builder.add_edge("finance_expert", "war_room")
    builder.add_edge("brand_expert", "war_room")
    builder.add_edge("marketing_expert", "war_room")

    # 6. War Room -> Writer
    builder.add_edge("war_room", "writer")

    # 7. Writer -> End
    builder.add_edge("writer", END)

    if memory is None:
        memory = MemorySaver()

    return builder.compile(checkpointer=memory)

if __name__ == "__main__":
    graph = build_dynamic_graph()
    print("\nDYNAMIC COUNCIL GRAPH STRUCTURE")
    try:
        print(graph.get_graph().draw_ascii())
    except Exception:
        pass
