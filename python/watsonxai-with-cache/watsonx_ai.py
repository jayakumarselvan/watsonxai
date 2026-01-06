import os

from dotenv import load_dotenv
from langchain_ibm import WatsonxLLM


load_dotenv()


class WatsonxAiService:
    def __init__(self):
        self.model = os.getenv("WATSONX_AI_DEFAULT_MODEL")
        self.watsonx_api_endpoint = os.getenv("WATSONX_API_ENDPOINT")
        self.watsonx_project_id = os.getenv("WATSONX_PROJECT_ID")
        self.watsonx_apikey = os.getenv("WATSONX_API_KEY")
        self.parameters_decoding_method = "greedy"
        self.parameters_max_new_tokens = 1000
        self.parameters_min_new_tokens = 1
        self.parameters_temperature = 0.5
        self.parameters_top_k = 50
        self.parameters_top_p = 1

    def get_watsonx_llm(self):
        parameters = {
            "decoding_method": self.parameters_decoding_method,
            "max_new_tokens": self.parameters_max_new_tokens,
            "min_new_tokens": self.parameters_min_new_tokens,
            "temperature": self.parameters_temperature,
            "top_k": self.parameters_top_k,
            "top_p": self.parameters_top_p,
        }

        watsonx_llm = WatsonxLLM(
            model_id=self.model,
            url=self.watsonx_api_endpoint,
            project_id=self.watsonx_project_id,
            apikey=self.watsonx_apikey,
            params=parameters,
        )
        return watsonx_llm
