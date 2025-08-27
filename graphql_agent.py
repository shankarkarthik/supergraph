# app/agents/graphql_agent.py
from typing import TypedDict, Annotated, List, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
import requests
import json

# Configuration
GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"


# Define the agent state
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]


# Initialize the language model with the latest client
llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)


# Define GraphQL tool
@tool
def execute_graphql(query: str) -> str:
    """Execute a GraphQL query and return the result as a string."""
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            json={"query": query},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        return f"Error executing GraphQL query: {str(e)}"


# Create the agent function
def agent_node(state: AgentState) -> dict:
    """Process messages and generate responses."""
    messages = state["messages"]

    if not messages:
        return {"messages": [AIMessage(content="How can I assist you with the GraphQL API?")]}

    # Get the last user message
    user_message = next((m for m in reversed(messages) if isinstance(m, HumanMessage)), None)
    if not user_message:
        return {"messages": [AIMessage(content="Please provide a query or request.")]}

    # Simple router to handle different types of queries
    user_input = user_message.content.lower()

    if any(keyword in user_input for keyword in ["get", "fetch", "list", "find"]):
        # Generate a GraphQL query based on the user's request
        query = f"""
        query {{
            leads {{
                id
                name
                email
                leadStatus
            }}
        }}
        """
        result = execute_graphql.invoke(query)
        return {"messages": [AIMessage(content=f"Here are the leads:\n{result}")]}

    elif any(keyword in user_input for keyword in ["create", "add", "new"]):
        # This is a simplified example - in a real app, you'd parse the input
        # and generate the appropriate mutation
        return {"messages": [AIMessage(content="To create a new record, please use the specific GraphQL mutation.")]}

    else:
        # For other queries, use the LLM to generate a response
        response = llm.invoke(messages)
        return {"messages": [response]}


# Create the workflow
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.set_entry_point("agent")
workflow.set_finish_point("agent")  # Simplified to a single node for now

# Compile the workflow
app = workflow.compile()


def create_react_agent():
    """Create and return a ReAct agent with GraphQL capabilities."""
    return app


# Example usage
if __name__ == "__main__":
    agent = create_react_agent()

    # Example conversation
    state = {
        "messages": [HumanMessage(content="Get all leads")],
    }

    # Run the agent
    for output in agent.stream(state):
        for key, value in output.items():
            print(f"Node: {key}")
            if "messages" in value:
                for msg in value["messages"]:
                    print(f"{type(msg).__name__}: {msg.content}")
            print("---")