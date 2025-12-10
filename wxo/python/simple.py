import os
import requests
import uuid
from dotenv import load_dotenv

load_dotenv()

WXO_API_KEY = os.getenv("WXO_API_KEY")
WXO_API_BASE_URL = os.getenv("WXO_API_BASE_URL")
WXO_AGENT_ID_FAQ = os.getenv("WXO_AGENT_ID_FAQ")
api_token_url = "https://iam.cloud.ibm.com/identity/token"


def call_wxo_agent(user_input):
    token_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token_payload = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": WXO_API_KEY,
    }
    token_response = requests.request(
        "POST", api_token_url, data=token_payload, headers=token_headers
    )
    token_response = token_response.json()
    access_token = token_response["access_token"]
    x_ibm_thread_i = str(uuid.uuid4())
    agent_url = f"{WXO_API_BASE_URL}{WXO_AGENT_ID_FAQ}/chat/completions"
    agent_payload = {
        "messages": [{"role": "user", "content": user_input}],
        "additional_parameters": {},
        "context": {},
        "stream": False,
    }
    agent_headers = {
        "Content-Type": "application/json",
        "X-IBM-THREAD-ID": x_ibm_thread_i,
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.request(
        "POST", agent_url, json=agent_payload, headers=agent_headers
    )
    response_json = response.json()
    content = response_json.get("choices", [{}])[0].get("message", {}).get("content")
    return content


# user_input = "How do I manage cash flow in my business?"
user_input = input("Enter your question: ")
agent_result = call_wxo_agent(user_input)

print(("-" * 25), "User Input", ("-" * 25))
print(user_input)
print(("-" * 25), "Agent Result", ("-" * 25))
print(agent_result)
print(("-" * 50))
