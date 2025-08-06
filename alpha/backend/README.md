## Alpha Backend
- Added audio summarizer using Watson Speech-to-Text and Watsonx LLM

## Create and Activate a Virtual Environment
```
python3 -m venv .venv
source .venv/bin/activate
```

## Install Dependencies
```
pip install -r requirements.txt
```

## .env Configuration
Refer to .env.sample for environment variable setup.

## Run the App
```
uvicorn app.main:app --reload
```