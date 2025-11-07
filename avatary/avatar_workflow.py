#!/usr/bin/env python3
"""
Avatar Workflow Visualization using LangGraph
Shows the complete flow: Connection → Vision → Recognition → Response
"""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator


class AvatarState(TypedDict):
    """State for avatar workflow"""
    user_connected: bool
    camera_enabled: bool
    frame_captured: bytes
    visual_analysis: str
    person_recognized: bool
    person_name: str
    user_message: str
    avatar_response: str
    context_injected: bool


def connect_user(state: AvatarState) -> AvatarState:
    """User connects to avatar"""
    print("🔌 User connecting...")
    state["user_connected"] = True
    state["camera_enabled"] = True
    print("✅ User connected, camera enabled")
    return state


def send_greeting(state: AvatarState) -> AvatarState:
    """Avatar sends initial greeting"""
    print("👋 Avatar: السلام عليكم! أهلاً بك في أورنينا")
    state["avatar_response"] = "Initial greeting sent"
    return state


def capture_frame(state: AvatarState) -> AvatarState:
    """Capture frame from camera every 3 seconds"""
    if state.get("camera_enabled"):
        print("📸 Capturing frame from camera...")
        state["frame_captured"] = b"frame_data"  # Simulated
        print("✅ Frame captured")
    return state


def analyze_vision(state: AvatarState) -> AvatarState:
    """GPT-4 Vision analyzes what user is doing"""
    if state.get("frame_captured"):
        print("👁️  GPT-4 Vision analyzing frame...")
        state["visual_analysis"] = "User is sitting at desk, holding phone"
        print(f"   Analysis: {state['visual_analysis']}")
    return state


def recognize_face(state: AvatarState) -> AvatarState:
    """Face recognition identifies the person"""
    if state.get("frame_captured"):
        print("🔍 Running face recognition...")
        # Simulated face recognition
        state["person_recognized"] = True
        state["person_name"] = "أحمد محمد"
        print(f"   👤 Recognized: {state['person_name']}")
    return state


def inject_context(state: AvatarState) -> AvatarState:
    """Inject visual + identity context into LLM"""
    context = []

    if state.get("visual_analysis"):
        context.append(f"Visual: {state['visual_analysis']}")

    if state.get("person_recognized"):
        context.append(f"Person: {state['person_name']}")

    if context:
        print("💉 Injecting context into LLM:")
        for c in context:
            print(f"   - {c}")
        state["context_injected"] = True

    return state


def wait_for_speech(state: AvatarState) -> AvatarState:
    """Wait for user to speak"""
    print("🎤 Listening for user speech (VAD)...")
    state["user_message"] = "مرحبا، كيف حالك؟"  # Simulated
    print(f"   User said: {state['user_message']}")
    return state


def generate_response(state: AvatarState) -> AvatarState:
    """LLM generates response with context"""
    print("🤖 LLM generating response...")
    print(f"   Context injected: {state.get('context_injected', False)}")

    if state.get("person_recognized"):
        response = f"أهلاً {state['person_name']}! أراك تحمل هاتفك. كيف أساعدك؟"
    else:
        response = "أهلاً! كيف أساعدك اليوم؟"

    state["avatar_response"] = response
    print(f"   Response: {response}")
    return state


def speak_response(state: AvatarState) -> AvatarState:
    """TTS speaks the response"""
    if state.get("avatar_response"):
        print(f"🔊 Avatar speaking: {state['avatar_response']}")
        print("   Using OpenAI TTS (alloy voice)")
    return state


def should_continue(state: AvatarState) -> str:
    """Decide if conversation should continue"""
    if state.get("user_connected"):
        return "continue"
    return "end"


# Create the workflow graph
workflow = StateGraph(AvatarState)

# Add nodes
workflow.add_node("connect", connect_user)
workflow.add_node("greeting", send_greeting)
workflow.add_node("capture", capture_frame)
workflow.add_node("vision", analyze_vision)
workflow.add_node("recognize", recognize_face)
workflow.add_node("inject", inject_context)
workflow.add_node("listen", wait_for_speech)
workflow.add_node("respond", generate_response)
workflow.add_node("speak", speak_response)

# Add edges (workflow flow)
workflow.set_entry_point("connect")
workflow.add_edge("connect", "greeting")
workflow.add_edge("greeting", "capture")
workflow.add_edge("capture", "vision")
workflow.add_edge("vision", "recognize")
workflow.add_edge("recognize", "inject")
workflow.add_edge("inject", "listen")
workflow.add_edge("listen", "respond")
workflow.add_edge("respond", "speak")

# Loop back to capture for continuous monitoring
workflow.add_conditional_edges(
    "speak",
    should_continue,
    {
        "continue": "capture",
        "end": END
    }
)

# Compile the graph
app = workflow.compile()


def visualize_workflow():
    """Generate and save workflow diagram"""
    try:
        from IPython.display import Image, display

        # Get the graph visualization
        graph_image = app.get_graph().draw_mermaid_png()

        # Save to file
        with open("avatar_workflow.png", "wb") as f:
            f.write(graph_image)

        print("✅ Workflow diagram saved to: avatar_workflow.png")
        return graph_image

    except Exception as e:
        print(f"⚠️  Could not generate image: {e}")
        print("   Install: pip install pygraphviz")

        # Print mermaid diagram instead
        print("\n📊 Workflow (Mermaid format):")
        print(app.get_graph().draw_mermaid())


def run_simulation():
    """Run a simulated conversation flow"""
    print("\n" + "="*60)
    print("🎬 AVATAR WORKFLOW SIMULATION")
    print("="*60 + "\n")

    # Initial state
    initial_state = {
        "user_connected": False,
        "camera_enabled": False,
        "frame_captured": None,
        "visual_analysis": "",
        "person_recognized": False,
        "person_name": "",
        "user_message": "",
        "avatar_response": "",
        "context_injected": False
    }

    # Run workflow for one cycle
    config = {"recursion_limit": 10}

    print("Starting workflow...\n")

    # Invoke the workflow
    for i, state in enumerate(app.stream(initial_state, config)):
        step_name = list(state.keys())[0]
        print(f"\nStep {i+1}: {step_name}")
        print("-" * 40)

        # Stop after one full cycle (speak step)
        if step_name == "speak":
            break

    print("\n" + "="*60)
    print("✅ Workflow simulation complete!")
    print("="*60)


if __name__ == "__main__":
    print("🔄 Avatar Workflow with LangGraph\n")

    # Visualize the workflow
    print("1. Generating workflow diagram...")
    visualize_workflow()

    print("\n" + "="*60 + "\n")

    # Run simulation
    print("2. Running workflow simulation...")
    run_simulation()

    print("\n📝 Workflow Summary:")
    print("""
    1. User connects → Camera enabled
    2. Avatar greets → "السلام عليكم!"
    3. Frame captured every 3s
    4. GPT-4 Vision analyzes what user is doing
    5. Face recognition identifies who they are
    6. Context injected into LLM
    7. User speaks (VAD detects)
    8. LLM generates response with context
    9. TTS speaks response
    10. Loop back to step 3 (continuous)

    🎯 Result: Avatar recognizes you by name and sees what you're doing!
    """)
