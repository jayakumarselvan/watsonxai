
#### Setup
```bash
python3.13 -m venv .venv
source .venv/bin/activate

pip install google-adk
pip install mcp
pip install langchain_mcp_adapters
pip install litellm
pip install python-dotenv
adk create watsonx-mcp
```

#### Run
```bash
cd watsonx-mcp
python agent.py
```




