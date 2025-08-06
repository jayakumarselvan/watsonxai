import asyncio
import sys
import traceback

from beeai_framework.agents.react import ReActAgent, ReActAgentRunOutput
from beeai_framework.backend import ChatModel
from beeai_framework.errors import FrameworkError
from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.tools.search.duckduckgo import DuckDuckGoSearchTool
from beeai_framework.tools.weather import OpenMeteoTool


async def main(user_input) -> None:
    llm = ChatModel.from_name("watsonx:meta-llama/llama-3-3-70b-instruct")
    agent = ReActAgent(
        llm=llm,
        tools=[DuckDuckGoSearchTool(), OpenMeteoTool()],
        memory=UnconstrainedMemory(),
    )

    output: ReActAgentRunOutput = await agent.run(user_input).on(
        "update",
        lambda data, event: print(
            f"Agent({data.update.key}) 🤖 : ", data.update.parsed_value
        ),
    )
    print("-" * 25)
    print("Agent 🤖 : ", output.result.text)
    print("-" * 25)


if __name__ == "__main__":
    try:
        user_input = "What's the current weather in Las Vegas?"
        asyncio.run(main(user_input))
    except FrameworkError as e:
        traceback.print_exc()
        sys.exit(e.explain())
