import warnings
import json

# Suppress noisy LangChain/LangGraph warnings
warnings.filterwarnings(
    "ignore",
    module="langchain_core"
)

warnings.filterwarnings(
    "ignore",
    module="langgraph"
)

from langgraph.graph import StateGraph, MessagesState, START, END


# -----------------------------
# Mock LLM Node
# -----------------------------
def mock_llm(state: MessagesState):
    return {
        "messages": [
            {
                "role": "ai",
                "content": "hello world"
            }
        ]
    }


# -----------------------------
# Helper Functions
# -----------------------------
def serialize_messages(messages):
    """
    Convert LangChain message objects
    into clean JSON serializable dicts.
    """

    serialized = []

    for msg in messages:
        serialized.append({
            "role": msg.type,
            "content": msg.content,
            "agent": getattr(msg, "name", None)
        })

    return serialized


def display_conversation(messages):
    """
    Pretty terminal renderer.
    """

    print("\n" + "=" * 60)
    print("CONVERSATION")
    print("=" * 60)

    for idx, msg in enumerate(messages, 1):

        print(f"\n[{idx}] {msg.type.upper()}")

        if hasattr(msg, "name") and msg.name:
            print(f"Agent: {msg.name}")

        print(f"Content: {msg.content}")

    print("\n" + "=" * 60)


# -----------------------------
# Build Graph
# -----------------------------
graph = StateGraph(MessagesState)

graph.add_node("mock_llm", mock_llm)

graph.add_edge(START, "mock_llm")
graph.add_edge("mock_llm", END)

app = graph.compile()


# -----------------------------
# Invoke Graph
# -----------------------------
user_input = input("\n💬 Enter your message: ")

result = app.invoke({
    "messages": [
        {
            "role": "user",
            "content": user_input
        }
    ]
})


# -----------------------------
# Pretty Terminal Output
# -----------------------------
display_conversation(result["messages"])


# -----------------------------
# Clean JSON Output
# -----------------------------
display_output = {
    "messages": serialize_messages(result["messages"])
}

print("\nJSON OUTPUT")
print("=" * 60)

print(json.dumps(display_output, indent=2))

print("=" * 60)