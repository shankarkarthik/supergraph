# app/agents/graphql_agent.py
from typing import TypedDict, Annotated, List, Literal, Union
from enum import Enum
import json
import requests
from pydantic import BaseModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

# Configuration
GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"


# Define the agent state
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]
    user_query: str


# Initialize the language model
llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)


# Define GraphQL tool
@tool
def execute_graphql(query: str, variables: dict = None) -> str:
    """Execute a GraphQL query against the API and return the result as a string."""
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            json={"query": query, "variables": variables or {}},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        return f"Error executing GraphQL query: {str(e)}"


# Define the agent function
def agent(state: AgentState) -> dict:
    """Agent node that processes messages and decides the next step."""
    messages = state["messages"]
    last_message = messages[-1]

    if not messages:
        return {"messages": [AIMessage(content="How can I help you with the GraphQL API?")]}

    # If the last message is from the user, process it
    if isinstance(last_message, HumanMessage):
        # Here we'll use the LLM to decide what to do
        response = llm.invoke([
            *messages,
            AIMessage(content="You are a helpful assistant that can execute GraphQL queries. "
                              "When you need to query the GraphQL API, use the execute_graphql tool. "
                              "The GraphQL endpoint is already configured. "
                              "Always format your queries properly and handle any errors gracefully.")
        ])
        return {"messages": [response]}

    # If the last message is from the assistant, check if we need to execute a tool
    elif isinstance(last_message, AIMessage):
        # Check if the message contains tool calls
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            # Get the first tool call
            tool_call = last_message.tool_calls[0]
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            # Execute the tool
            if tool_name == "execute_graphql":
                result = execute_graphql.invoke(tool_args)
                return {"messages": [ToolMessage(content=result, tool_call_id=tool_call["id"])]}

    # Default case - just return the messages
    return {"messages": messages}


# Define tool execution node
def tool_node(state: AgentState) -> dict:
    """Node that executes tools based on the last message."""
    messages = state["messages"]
    last_message = messages[-1]

    # If the last message is a tool message, we're done
    if isinstance(last_message, ToolMessage):
        return state

    # Otherwise, execute the tool
    if hasattr(last_message, "tool_calls"):
        tool_call = last_message.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        if tool_name == "execute_graphql":
            result = execute_graphql.invoke(tool_args)
            return {"messages": [ToolMessage(content=result, tool_call_id=tool_call["id"])]}

    return state


# Define the router
def router(state: AgentState) -> Literal["tools", "agent", "__end__"]:
    """Router function that decides the next node to execute."""
    messages = state["messages"]
    last_message = messages[-1]

    # If the last message is from the user, go to the agent
    if isinstance(last_message, HumanMessage):
        return "agent"

    # If the last message is from the assistant and has tool calls, go to tools
    if isinstance(last_message, AIMessage) and hasattr(last_message, "tool_calls"):
        return "tools"

    # Otherwise, we're done
    return "__end__"


# Create the workflow
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", agent)
workflow.add_node("tools", tool_node)

# Add edges
workflow.add_conditional_edges(
    "agent",
    router,
    {
        "tools": "tools",
        "agent": "agent",
        "__end__": END
    }
)

workflow.add_edge("tools", "agent")

# Set the entry point
workflow.set_entry_point("agent")

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