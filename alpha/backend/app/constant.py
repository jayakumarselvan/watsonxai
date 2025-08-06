import os
from dotenv import load_dotenv

load_dotenv()

WATSONX_APIKEY = os.getenv("WATSONX_APIKEY")
WATSONX_URL = os.getenv("WATSONX_URL")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")

WATSONX_MODEL_ID = "meta-llama/llama-3-3-70b-instruct"

WATSONX_S2T_APIKEY = os.getenv("WATSONX_S2T_APIKEY")
WATSONX_S2T_URL = os.getenv("WATSONX_S2T_URL")
