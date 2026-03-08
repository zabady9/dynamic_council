import os
import sys
import time
import uuid
from datetime import datetime
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

from graph import build_dynamic_graph
from langgraph.checkpoint.memory import MemorySaver

def print_header():
    print("\n" + "="*65)
    print("  DYNAMIC CONSULTANT COUNCIL (Conversational & Outline-First)")
    print("  Powered by LangGraph + Gemini")
    print("="*65)
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*65 + "\n")

def run_interactive_engagement():
    if not os.environ.get("GOOGLE_API_KEY"):
        raise ValueError("GOOGLE_API_KEY not found in .env file")

    print_header()

    # Initialize graph with memory
    memory = MemorySaver()
    graph = build_dynamic_graph(memory)
    
    # Unique thread ID for this conversation
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print("🤖 INTAKE SPECIALIST: Hello! / مرحباً!")
    print("   Please describe your project, industry, and core problem in your preferred language.")
    print("   برجاء وصف مشروعك، مجالك، والمشكلة الأساسية باللغة التي تفضلها.")
    print("   (Press Enter twice to submit / اضغط Enter مرتين للإرسال)\n")

    while True:
        # Get user input
        lines = []
        while True:
            line = input("👤 YOU: " if not lines else "        ")
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        
        user_input = "\n".join(lines).strip()
        if not user_input:
            print("Please provide some details.")
            continue

        if user_input.lower() in ['exit', 'quit']:
            print("\nGoodbye!")
            break

        state_update = {"messages": [HumanMessage(content=user_input)]}

        start_time = time.time()
        
        # We only print the header once when the full execution starts
        execution_started = False

        for step in graph.stream(state_update, config, stream_mode="updates"):
            for node_name, node_output in step.items():
                if node_name == "collector":
                    if node_output.get("requirements_met"):
                        ai_msgs = node_output.get("messages", [])
                        if ai_msgs:
                            print(f"\n🤖 INTAKE SPECIALIST: {ai_msgs[-1].content}")
                else:
                    if not execution_started:
                        print("\n🚀 Starting Full Dynamic Council Execution...\n")
                        execution_started = True

                    if node_name == "supervisor":
                        print(f"👔 SUPERVISOR (Engagement Manager)")
                        print(f"   ↳ Generated Master Outline")
                        print(f"   ↳ Activated Team: {', '.join(node_output.get('active_agents', []))}\n")
                    
                    elif node_name.endswith("_expert"):
                        print(f"🧠 {node_name.upper()}")
                        print(f"   ↳ Research complete. Bullet points submitted.\n")
                        
                    elif node_name == "war_room":
                        print(f"⚖️  WAR ROOM (Strategy Director)")
                        print(f"   ↳ Analyzed agent outputs. Contradictions resolved.\n")
                        
                    elif node_name == "writer":
                        print(f"✍️  MASTER WRITER")
                        print(f"   ↳ Final document drafted.\n")
                        
                    elif node_name == "rewriter":
                        print(f"✨ QUERY REWRITER")
                        print(f"   ↳ Master Project Brief generated from history.\n")

        # After stream finishes, get the current state
        final_state = graph.get_state(config).values

        if final_state.get("requirements_met"):
            duration = time.time() - start_time
            print("="*65)
            print(f"  ✅ ENGAGEMENT COMPLETE ({duration:.1f} seconds)")
            print("="*65 + "\n")

            # Save outputs
            results_dir = "results"
            if not os.path.exists(results_dir):
                os.makedirs(results_dir)
                
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save Document
            doc_filename = os.path.join(results_dir, f"document_{timestamp}.txt")
            with open(doc_filename, "w", encoding="utf-8") as f:
                f.write(final_state.get("final_document", ""))
            
            # Save Refined Brief
            brief_filename = os.path.join(results_dir, f"refined_brief_{timestamp}.txt")
            with open(brief_filename, "w", encoding="utf-8") as f:
                f.write(final_state.get("refined_query", ""))

            print(f"💾 Final document saved to: {doc_filename}")
            print(f"💾 Refined Master Brief saved to: {brief_filename}\n")
            
            print("FINAL DOCUMENT PREVIEW (first 500 chars):")
            print("-" * 65)
            print(final_state.get("final_document", "")[:500] + "...\n")
            
            print("🤖 INTAKE SPECIALIST: Your report is ready! Would you like to add or modify anything? / تقريرك جاهز! هل تود إضافة أو تعديل أي شيء؟ (Type 'exit' to quit)\n")
            
        else:
            # Requirements not met, print the AI's question and continue the loop
            ai_messages = [m for m in final_state.get("messages", []) if isinstance(m, AIMessage)]
            if ai_messages:
                last_ai_msg = ai_messages[-1].content
                print(f"\n🤖 INTAKE SPECIALIST: {last_ai_msg}\n")
            else:
                print("\n🤖 INTAKE SPECIALIST: Could you provide more details?\n")

if __name__ == "__main__":
    try:
        run_interactive_engagement()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
        sys.exit(0)
