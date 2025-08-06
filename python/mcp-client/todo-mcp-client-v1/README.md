

🧰 Set Up Your Python Environment

- dotenv – Loads environment variables from a .env file into os.environ, making it easier to manage secrets and configuration settings in development.
- langchain-ibm – Integrates IBM WatsonX models into LangChain, enabling advanced LLM capabilities with WatsonX's APIs for text generation and chat.
- langchain-mcp-adapters – Adds support for using MCP (Multi-Chain Protocol) tools and agents within LangChain workflows, enabling distributed, multi-agent orchestration.
- langgraph – A framework built on top of LangChain that helps structure LLM applications as stateful, multi-agent graphs, allowing better control over AI workflows.
- mcp – Helps you build AI-powered tools and servers quickly, making it easy to run LLM-based workflows with Python.

```
uv init todo-mcp-client
uv add dotenv langchain-ibm langchain-mcp-adapters langgraph mcp
```

Execute the below command to run:

```bash
python client.py
```