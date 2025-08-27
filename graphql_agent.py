# app/agents/graphql_agent.py
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
import requests
import json

# Configuration
GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"


# Define the agent state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_query: str


# Initialize the language model
llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)


# Define GraphQL tool
@tool
def execute_graphql(query: str, variables: dict = None) -> dict:
    """Execute a GraphQL query against the API."""
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            json={"query": query, "variables": variables or {}},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


# Define the agent nodes
def should_continue(state: AgentState) -> str:
    """Determine if the agent should continue or finish."""
    messages = state["messages"]
    last_message = messages[-1]

    # If the last message is from the assistant, we're done
    if isinstance(last_message, AIMessage):
        return "end"
    return "continue"


def call_model(state: AgentState) -> dict:
    """Call the language model to generate a response or GraphQL query."""
    messages = state["messages"]

    # If there are no messages, ask for input
    if not messages:
        return {"messages": [AIMessage(content="How can I help you with the GraphQL API?")]}

    # Check if we need to execute a GraphQL query
    last_message = messages[-1]
    if "execute_graphql" in last_message.content:
        query = last_message.content.replace("execute_graphql", "").strip()
        result = execute_graphql(query)
        return {"messages": [AIMessage(content=f"GraphQL result: {json.dumps(result, indent=2)}")]}

    # Otherwise, generate a response
    response = llm.invoke(messages)
    return {"messages": [response]}


# Create the workflow
workflow = StateGraph(AgentState)

# Define the nodes
workflow.add_node("agent", call_model)
workflow.add_node("action", execute_graphql)

# Define the edges
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "action",
        "end": END
    }
)
workflow.add_edge("action", "agent")

# Set the entry point
workflow.set_entry_point("agent")

# Compile the graph
app = workflow.compile()


def create_react_agent():
    """Create and return a ReAct agent with GraphQL capabilities."""
    return app


# Example usage
if __name__ == "__main__":
    # Initialize the agent
    agent = create_react_agent()

    # Example conversation
    state = {
        "messages": [HumanMessage(content="Get all leads")],
        "user_query": "Get all leads"
    }

    # Run the agent
    for output in agent.stream(state):
        for key, value in output.items():
            print(f"Node: {key}")
            if "messages" in value:
                for msg in value["messages"]:
                    print(f"{type(msg).__name__}: {msg.content}")
            print("---")