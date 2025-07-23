import asyncio
import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ibm import ChatWatsonx
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent

load_dotenv()

parameters = {
    "temperature": 0.9,
    "max_tokens": 1000,
}

watsonx_llm = ChatWatsonx(
    model_id=os.getenv("WATSONX_MODEL_ID"),
    url=os.getenv("WATSONX_URL"),
    project_id=os.getenv("WATSONX_PROJECT_ID"),
    params=parameters,
)


async def main():
    client = MultiServerMCPClient(
        {
            "todo": {
                "url": "http://127.0.0.1:8002/sse",
                "transport": "sse",
            },
        }
    )

    # Discover available tools from the MCP server
    tools = await client.get_tools()

    agent = create_react_agent(watsonx_llm, tools)

    agent_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Create a todo task for Make bed"}]}
    )
    print("agent response:", agent_response["messages"][-1].content)

    agent_response = await agent.ainvoke(
        {
            "messages": [
                {"role": "user", "content": "Create a todo task for Quick exercise"}
            ]
        }
    )
    print("agent response:", agent_response["messages"][-1].content)

    agent_response = await agent.ainvoke(
        {
            "messages": [
                {"role": "user", "content": "Create a todo task for Attend meetings"}
            ]
        }
    )
    print("agent response:", agent_response["messages"][-1].content)

    agent_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Create a todo task for Review PR"}]}
    )
    print("agent response:", agent_response["messages"][-1].content)

    agent_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Summarize the tasks"}]}
    )
    print("agent response:", agent_response["messages"][-1].content)

    agent_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "complete my todo: Make bed"}]}
    )
    print("agent response:", agent_response["messages"][-1].content)

    agent_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "complete my todo: Quick exercise"}]}
    )
    print("agent response:", agent_response["messages"][-1].content)

    agent_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Summarize the tasks"}]}
    )
    print("agent response:", agent_response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
