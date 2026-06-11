
# City Time Reporter Agent

An automated workflow built with the **Google ADK (Agent Development Kit)** and **Watsonx AI** that generates a random city, simulates looking up its current time, and prints a formatted localized time report.

## Prerequisite Installation

Before running the agent, make sure you have the required packages installed in your Python environment:

```bash
python3.13 -m venv .venv
source .venv/bin/activate

pip install google-adk
pip install litellm
```

Getting Started
1. Initialize the Project
If you haven't created the project directory yet, generate the boilerplate scaffold using the ADK CLI:
```bash
adk create city_time_reporter
```

2. Set Up the Code
Replace the contents of your city_time_reporter/agent.py file with the completed workflow code.

3. Run the Agent
Execute the agent interactively from your terminal:
```bash
adk run city_time_reporter
```
4. Result
```bash
Running agent root_agent, type exit to exit.
[user]: Chennai
09:40:20 - LiteLLM:INFO: utils.py:4083 - 
LiteLLM completion() model= meta-llama/llama-3-3-70b-instruct; provider = watsonx
[city_generator_agent]: { 
  "city_name": "Mumbai"
}
09:40:22 - LiteLLM:INFO: utils.py:4083 - 
LiteLLM completion() model= meta-llama/llama-3-3-70b-instruct; provider = watsonx
[city_report_agent]: It is 10:10 AM in Mumbai right now.
[root_agent]: It is 10:10 AM in Mumbai right now.
WORKFLOW COMPLETED.
 ```

#### Workflow Architecture
The agent executes a linear 4-step pipeline:

- city_generator_agent: Uses a llama-3-3-70b-instruct model to pick a random city.
- lookup_time_function: A Python node that structures the city and maps its current time info.
- city_report_agent: Formats the final text output dynamically.
- completed_message_function: Emits the final success log event.