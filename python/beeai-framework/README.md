#### 🚀 Just built a simple AI-powered Weather Agent using the [beeai-framework] and IBM’s watsonx.ai LLMs! 🌤️🤖

🧰 Set Up Your Python Environment

- beeai-framework - helps you build lightweight AI apps and assistants with ease.
- Optional integration like duckduckgo lets your assistant search the web for smarter responses.


```
# 📦 Create and activate your virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 🚀 Install the base framework
pip install beeai-framework

# 🔍 Add optional web search capability
pip install "beeai-framework[duckduckgo]"
```

Execute the below command to run:

```
python simple.py
```

Output
```
Agent 🤖 :  The current weather in Las Vegas is 96°F with a relative humidity of 10% and a wind speed of 13.5 km/h.
```