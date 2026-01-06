
### Importing agents using an agent file

#### 🔧 Setup

##### Create a virtual environment
```
python3 -m venv .venv
```

##### Activate the virtual environment
```
source .venv/bin/activate
```

##### Install required packages
```
pip install ibm-watsonx-orchestrate
```

Check the orchestrate version
```
orchestrate --version
```

Add and activate your environment with the ADK CLI
```
orchestrate env add -n wxo-demo1 -u <orchestrate_url> --type ibm_iam --activate
```

List Environments
```
orchestrate env list
```

Import the Tool
```
orchestrate tools import -k python -f greeting_tool.py
```

Import the agent
```
orchestrate agents import -f greeting_agent.yaml
```

Import the toolkits
```
orchestrate toolkits import --kind mcp --name todo-mcp-demo-1 --description "todo-mcp"  --url "<YOUR_MCP_SERVER_ENDPOINT>/sse"  --transport "sse" --tools "tool1,tool2,tool3"
```

