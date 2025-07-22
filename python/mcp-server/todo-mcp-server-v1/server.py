# server.py
import json
import os
from dotenv import load_dotenv

load_dotenv()
from mcp.server.fastmcp import FastMCP
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import Credentials

# Create an MCP server
mcp = FastMCP("Demo")

# Load Watsonx Credentials
credentials = Credentials(
    api_key=os.getenv("WATSONX_API_KEY"), url=os.getenv("WATSONX_URL")
)
model_id = os.getenv("WATSONX_MODEL_ID")
project_id = os.getenv("WATSONX_PROJECT_ID")
llm = ModelInference(model_id=model_id, credentials=credentials, project_id=project_id)


# File for persistence
TASK_FILE = "tasks.json"


# -------------------
# Task persistence helpers
# -------------------
def load_tasks():
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, "r") as f:
            return json.load(f)
    return []


def save_tasks(tasks):
    with open(TASK_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


TASKS = load_tasks()


# Create a todo task
@mcp.tool()
def create_task(title):
    """Create a todo task"""
    TASKS.append({"title": title, "completed": False})
    save_tasks(TASKS)
    return "A task is created"


# Mark the task as completed
@mcp.tool()
def complete_task(title):
    """Mark the task as completed"""
    for task in TASKS:
        if task["title"].lower() == title.lower():
            task["completed"] = True
            break
    save_tasks(TASKS)
    return "Task marked as completed"


# Summarize the tasks
@mcp.tool()
def summarize_tasks():
    """Summarize the tasks"""

    task_list_json = json.dumps(TASKS, indent=2)

    prompt = f"""You are provided with a list of tasks in JSON format.
Your job is to generate a clear, well-structured Markdown summary that:
- Uses proper headings (## for main title, ### for sections)
- Lists pending and completed tasks under their respective sections
- Uses bullet points (-) for each task title
- Adds a checkmark (✅) emoji in the heading for completed tasks

Here is the task list:
```json
{task_list_json}

Respond only with a clean Markdown summary.
"""
    parameters = {
        "decoding_method": "greedy",
        "max_new_tokens": 1000,
        "min_new_tokens": 1,
    }

    response = llm.generate(prompt=prompt, params=parameters)
    return_data = response["results"][0]["generated_text"]
    return return_data


if __name__ == "__main__":
    # Expose via HTTP for client access
    # mcp.run(transport="streamable-http")
    mcp.run(transport="sse")
