# app/agents/graphql_agent.py
from typing import TypedDict, Annotated, Sequence, Literal
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode, tools_condition
import requests
import json
from enum import Enum

# Configuration
GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"


# Define the agent state
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], lambda x, y: x + y]
    user_query: str


# Define available tools
class AvailableTools(str, Enum):
    execute_graphql = "execute_graphql"


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


# Define the tool node
tools = [execute_graphql]
tool_node = ToolNode(tools)


# Define the agent
def agent(state: AgentState) -> dict:
    """Agent node that decides which tool to use or responds to the user."""
    messages = state["messages"]
    last_message = messages[-1]

    # If there are no messages, ask for input
    if not messages:
        return {"messages": [AIMessage(content="How can I help you with the GraphQL API?")]}

    # If the last message is from the user, process it
    if isinstance(last_message, HumanMessage):
        # Here you can add logic to decide whether to use a tool or respond directly
        # For now, we'll just pass it to the LLM
        response = llm.invoke(messages)
        return {"messages": [response]}

    # If the last message is from the assistant, check if it contains a tool call
    elif isinstance(last_message, AIMessage):
        # Check if the message contains a tool call
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            # Extract the tool calls
            tool_calls = last_message.tool_calls
            # For simplicity, we'll just take the first tool call
            tool_call = tool_calls[0]
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            # Execute the tool
            if tool_name == "execute_graphql":
                result = execute_graphql.invoke(tool_args)
                return {"messages": [AIMessage(content=f"GraphQL result: {json.dumps(result, indent=2)}")]}

        # If no tool calls, just return the message
        return {"messages": [last_message]}

    # Default case
    return {"messages": [AIMessage(content="I'm not sure how to process that request.")]}


# Create the workflow
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", agent)
workflow.add_node("tools", tool_node)

# Set the entry point
workflow.set_entry_point("agent")

# Add edges
workflow.add_conditional_edges(
    "agent",
    tools_condition,
)

workflow.add_edge("tools", "agent")

# Compile the workflow
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