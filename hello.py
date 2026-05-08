import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*pydantic.v1.*")
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)

from langgraph.graph import StateGraph, MessagesState, START, END
from pprint import pprint
import json

def mock_llm(state: MessagesState):
    return {
        "messages": [
            {
                "role": "ai",
                "content": "hello world"
            }
        ]
    }

graph = StateGraph(MessagesState)

graph.add_node("mock_llm", mock_llm)
graph.add_edge(START, "mock_llm")
graph.add_edge("mock_llm", END)

app = graph.compile()

result = app.invoke({
    "messages": [
        {
            "role": "user",
            "content": "hi!"
        }
    ]
})

print("\n" + "="*60)
print("FINAL STATE")
print("="*60)

# Extract messages
messages = result['messages']
user_msg = messages[0]
ai_msg = messages[-1]

print(f"\nInput Message: {user_msg.content}")
print(f"Output Message: {ai_msg.content}")
print(f"Message Type: {type(ai_msg).__name__}")
print("\n" + "="*60)
print("Full Response:")
print("="*60)
print(json.dumps({
    "messages": [
        {"role": m.type, "content": m.content}
        for m in messages
    ]
}, indent=2))