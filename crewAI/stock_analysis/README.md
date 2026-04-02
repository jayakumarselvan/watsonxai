
## Create and Activate a Virtual Environment
```
python3.13 -m venv .venv
source .venv/bin/activate
```

## Install Dependencies
```
pip install -r requirements.txt
```

## .env Configuration
```
WATSONX_URL=
WATSONX_PROJECT_ID=
WATSONX_APIKEY=
```

## Run the application:
```
python main.py
python main.py TSLA
python main.py MSFT
python main.py NVDA
```