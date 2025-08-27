# app/agents/report_agent.py
from typing import TypedDict, List
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
import requests
import json
from datetime import datetime

# Configuration
GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"

# Initialize the language model
llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)


@tool
def execute_graphql(query: str) -> str:
    """Execute a GraphQL query and return the results as a string."""
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


@tool
def generate_report(data: str, report_type: str) -> str:
    """Generate a report based on the provided data and report type."""
    try:
        prompt = f"""
        Generate a {report_type} report based on the following data:

        {data}

        The report should be well-structured and include key insights.
        """

        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error generating report: {str(e)}"


# Define the tools
tools = [execute_graphql, generate_report]

# Create the agent
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt="""You are a helpful assistant that generates reports from GraphQL data.
    When asked to generate a report, first fetch the necessary data using execute_graphql,
    then use generate_report to format it into a professional report.
    Always confirm with the user if the report meets their needs.
    """
)


def generate_report_agent():
    """Create and return a report generation agent."""
    return agent


# Example usage
if __name__ == "__main__":
    from langchain_core.messages import HumanMessage, SystemMessage

    # Initialize the agent
    agent = generate_report_agent()

    # Example conversation
    messages = [
        SystemMessage(content="You are a helpful assistant that generates reports from GraphQL data."),
        HumanMessage(content="Generate a monthly sales report for August 2023")
    ]

    # Run the agent
    for chunk in agent.stream({"messages": messages}):
        if "messages" in chunk:
            for msg in chunk["messages"]:
                print(f"{msg.type}: {msg.content}")