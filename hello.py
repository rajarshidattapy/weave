from langgraph.graph import StateGraph, MessagesState, START, END
from pprint import pprint

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

print("\n=== FINAL STATE ===\n")
pprint(result)