import asyncio
import os
import sys
import inspect
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Official Google ADK 2.0 orchestration imports
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# FIXED: Import litellm directly to modify its default parameters for watsonx compatibility
import litellm

# Load secrets
load_dotenv()


async def main():
    if "MCP_ENDPOINT" not in os.environ or "MCP_AUTH_KEY" not in os.environ:
        print("Error: Missing MCP configuration in environment.", file=sys.stderr)
        return

    endpoint_url = os.environ["MCP_ENDPOINT"]
    mcp_auth_key = os.environ["MCP_AUTH_KEY"]
    mcp_authinstanceid = os.environ["MCP_AUTHINSTANCEID"]

    headers = {
        "Authorization": f"Basic {mcp_auth_key}",
        "authinstanceid": f"{mcp_authinstanceid}",
    }

    print("🔄 Connecting to watsonx.data Remote MCP Server...")

    async with streamablehttp_client(endpoint_url, headers=headers) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as mcp_session:
            await mcp_session.initialize()

            # Fetch remote tools exposed by watsonx.data
            remote_tools = await mcp_session.list_tools()
            adk_tools = []

            # Convert MCP server tools into standard python functions matching ADK standards
            for tool in remote_tools.tools:

                def create_mcp_wrapper(t_name, t_desc):
                    async def mcp_tool_wrapper(arguments: dict = None) -> str:
                        actual_args = arguments or {}
                        print(f"\n🔧 Calling tool: {t_name}")
                        print(f"📋 Arguments: {actual_args}")

                        try:
                            result = await asyncio.wait_for(
                                mcp_session.call_tool(t_name, arguments=actual_args),
                                timeout=30.0,  # 30 second timeout
                            )
                            print(f"✅ Tool {t_name} completed successfully")

                            if isinstance(result.content, list):
                                text_contents = [
                                    block.text
                                    for block in result.content
                                    if hasattr(block, "text")
                                ]
                                return "\n".join(text_contents)
                            return str(result.content)
                        except asyncio.TimeoutError:
                            error_msg = f"⏱️ Tool {t_name} timed out after 30 seconds"
                            print(error_msg)
                            return error_msg
                        except Exception as e:
                            error_msg = f"❌ Error calling tool {t_name}: {str(e)}"
                            print(error_msg)
                            return error_msg

                    mcp_tool_wrapper.__name__ = t_name
                    mcp_tool_wrapper.__doc__ = str(
                        t_desc or f"Execute database operation {t_name}"
                    )

                    mcp_tool_wrapper.__signature__ = inspect.Signature(
                        [
                            inspect.Parameter(
                                "arguments",
                                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                annotation=dict,
                                default=None,
                            )
                        ]
                    )
                    return mcp_tool_wrapper

                adk_tools.append(create_mcp_wrapper(tool.name, tool.description))

            print(
                f"✅ Successfully integrated {len(adk_tools)} tools from watsonx.data."
            )
            print("\n📋 Available tools:")
            for tool in remote_tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            print()

            # 1. FIXED: Tell LiteLLM to never send parallel tool configurations to watsonx
            # This strips or overrides the parameter causing the 400 bad request error.
            litellm.drop_params = True

            # Instantiate LiteLlm model with parallel execution disabled
            watsonx_model = LiteLlm(
                model="watsonx/meta-llama/llama-3-3-70b-instruct",
                # Pass directly to model completion argument mapping if supported by the wrapper
                parallel_tool_calls=False,
            )

            # 2. Instantiate the Core LlmAgent
            watsonx_agent = LlmAgent(
                model=watsonx_model,
                name="watsonx_data_explorer",
                instruction=(
                    "You are an enterprise database assistant with direct access to watsonx.data.\n\n"
                    "AVAILABLE TOOLS (use exact names):\n"
                    "- watsonxdata-list-engines: List available compute engines\n"
                    "- watsonxdata-list-schemas: List schemas in a catalog\n"
                    "- watsonxdata-list-tables: List tables in a schema\n"
                    "- watsonxdata-describe-table: Get detailed table structure and columns\n"
                    "- watsonxdata-execute-select: Execute SELECT queries (read-only)\n"
                    "- watsonxdata-execute-insert: Execute INSERT queries\n"
                    "- watsonxdata-execute-update: Execute UPDATE queries\n\n"
                    "MANDATORY WORKFLOW:\n"
                    "1. For listing catalogs/schemas:\n"
                    "   - Use watsonxdata-list-schemas with catalog_name and engine_id\n"
                    "   - Note: There is NO 'list-catalogs' tool - use list-schemas for each known catalog\n\n"
                    "2. For data queries - FOLLOW THIS SEQUENCE:\n"
                    "   Step A: If engine_id unknown, call watsonxdata-list-engines first\n"
                    "   Step B: Call watsonxdata-list-tables to see available tables\n"
                    "   Step C: Optionally call watsonxdata-describe-table to see column details\n"
                    "   Step D: Call watsonxdata-execute-select with SQL using ACTUAL table names from Step B\n\n"
                    "CRITICAL RULES:\n"
                    "- NEVER call 'watsonxdata-list-catalogs' - it doesn't exist!\n"
                    "- NEVER guess table names - ALWAYS list tables first\n"
                    "- Execute ONE tool at a time and wait for results\n"
                    "- All parameters must be in 'arguments' dict\n"
                    "- Use fully qualified table names: catalog.schema.table\n"
                    "- For execute-select, include: sql, catalog_name, schema_name, engine_id, limit\n\n"
                    "PARAMETER GUIDELINES:\n"
                    "- engine_id: Get from list-engines or use user-provided value\n"
                    "- catalog_name: Get from user query or list-schemas results\n"
                    "- schema_name: Get from user query or list-schemas results\n"
                    "- limit: Default to 500 for execute-select queries"
                ),
                tools=adk_tools,
            )

            # 3. Setup the session variables
            APP_NAME = "watsonx_explorer_app"
            USER_ID = "default_user"
            SESSION_ID = "session_001"

            session_service = InMemorySessionService()
            await session_service.create_session(
                app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
            )

            runner = Runner(
                agent=watsonx_agent, app_name=APP_NAME, session_service=session_service
            )

            print("\n=======================================================")
            print("💬 Chat session initialized using LiteLLM (watsonx.ai).")
            print("Type 'exit' or 'quit' to stop.")
            print("=======================================================\n")

            # Continuous interactive loop
            while True:
                try:
                    user_query = await asyncio.to_thread(input, "User 👤: ")
                except (KeyboardInterrupt, EOFError):
                    print("\nExiting...")
                    break

                if user_query.strip().lower() in ["exit", "quit"]:
                    print("Goodbye! Closing watsonx.data MCP session.")
                    break

                if not user_query.strip():
                    continue

                print("Agent 🤖 thinking...\n")

                try:
                    formatted_message = types.Content(
                        role="user", parts=[types.Part(text=user_query)]
                    )

                    response_started = False
                    async for event in runner.run_async(
                        user_id=USER_ID,
                        session_id=SESSION_ID,
                        new_message=formatted_message,
                    ):
                        # Debug: Print event type
                        print(f"[DEBUG] Event type: {type(event).__name__}", flush=True)

                        if not response_started:
                            print("Agent Response: ", end="", flush=True)
                            response_started = True

                        if (
                            hasattr(event, "is_final_response")
                            and event.is_final_response()
                        ):
                            if hasattr(event, "content") and event.content.parts:
                                print(event.content.parts[0].text, end="", flush=True)
                        elif hasattr(event, "text") and event.text:
                            print(event.text, end="", flush=True)
                        elif isinstance(event, str):
                            print(event, end="", flush=True)

                    print("\n" + "-" * 50)

                except asyncio.TimeoutError:
                    print(
                        f"\n⏱️ Request timed out. The agent may be stuck on a tool call.\n"
                    )
                except Exception as e:
                    print(f"\n❌ Error during execution: {e}")
                    import traceback

                    traceback.print_exc()
                    print()


if __name__ == "__main__":
    asyncio.run(main())
