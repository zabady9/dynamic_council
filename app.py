import streamlit as st
import uuid
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

from graph import build_dynamic_graph
from langgraph.checkpoint.memory import MemorySaver

# --- Page Config ---
st.set_page_config(page_title="Dynamic Consultant Council", page_icon="💼", layout="wide")

st.title("💼 Dynamic Consultant Council")
st.markdown("An AI-powered multi-agent system that dynamically scopes, researches, and writes executive consulting reports.")

# --- Graph Initialization ---
@st.cache_resource
def get_graph():
    memory = MemorySaver()
    return build_dynamic_graph(memory)

graph = get_graph()

# --- Session State Initialization ---
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! / مرحباً!\nPlease describe your project, industry, and core problem in your preferred language.\nبرجاء وصف مشروعك، مجالك، والمشكلة الأساسية باللغة التي تفضلها."}
    ]

# --- Display Chat History ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Chat Input ---
if prompt := st.chat_input("Type your message here... / اكتب رسالتك هنا..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process with LangGraph
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    state_update = {"messages": [HumanMessage(content=prompt)]}

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # We use a status container to show the agents working
        with st.status("Agents are thinking... / جاري التفكير...", expanded=True) as status:
            
            for step in graph.stream(state_update, config, stream_mode="updates"):
                for node_name, node_output in step.items():
                    if node_name == "collector":
                        if node_output.get("requirements_met"):
                            st.write("✅ **Intake Specialist**: Requirements gathered. Passing to Engagement Manager...")
                    elif node_name == "rewriter":
                        st.write("✨ **Query Rewriter**: Master Project Brief generated.")
                    elif node_name == "supervisor":
                        st.write("👔 **Supervisor**: Generated Master Outline & Activated Team: " + ", ".join(node_output.get('active_agents', [])))
                    elif node_name.endswith("_expert"):
                        st.write(f"🧠 **{node_name.replace('_', ' ').title()}**: Research complete.")
                    elif node_name == "war_room":
                        st.write("⚖️ **War Room**: Analyzed agent outputs. Contradictions resolved.")
                    elif node_name == "writer":
                        st.write("✍️ **Master Writer**: Final document drafted.")
                        
            status.update(label="Process Complete! / تمت العملية!", state="complete", expanded=False)

        # Get final state
        final_state = graph.get_state(config).values

        if final_state.get("requirements_met"):
            # Show the final document
            final_doc = final_state.get("final_document", "")
            message_placeholder.markdown(final_doc)
            st.session_state.messages.append({"role": "assistant", "content": final_doc})
            
            # Follow up message
            follow_up = "Your report is ready! Would you like to add or modify anything? / تقريرك جاهز! هل تود إضافة أو تعديل أي شيء؟"
            st.markdown(f"**{follow_up}**")
            st.session_state.messages.append({"role": "assistant", "content": follow_up})
            
        else:
            # Requirements not met, show collector's response
            ai_messages = [m for m in final_state.get("messages", []) if isinstance(m, AIMessage)]
            if ai_messages:
                last_ai_msg = ai_messages[-1].content
                message_placeholder.markdown(last_ai_msg)
                st.session_state.messages.append({"role": "assistant", "content": last_ai_msg})
            else:
                error_msg = "Could you provide more details? / هل يمكنك تقديم المزيد من التفاصيل؟"
                message_placeholder.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
