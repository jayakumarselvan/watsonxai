import os
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from dotenv import load_dotenv

from app import constant

load_dotenv()


class WatsonxService:
    def __init__(self):
        credentials = Credentials(
            api_key=constant.WATSONX_APIKEY,
            url=constant.WATSONX_URL,
        )
        self.model_id = constant.WATSONX_MODEL_ID
        self.project_id = constant.WATSONX_PROJECT_ID
        self.llm = ModelInference(
            model_id=self.model_id,
            credentials=credentials,
            project_id=self.project_id,
        )

    def generate_summary(self, text: str) -> str:
        prompt = f"""### Prompt: Summarize Transcript

Summarize the following transcript into a clear and concise summary.  
Focus on the **main points**, **key ideas**, and any **conclusions or recommendations**.  
Avoid filler or irrelevant details.

---

**Transcript:**

{text}
"""
        parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 1000,
            "min_new_tokens": 1,
        }

        response = self.llm.generate(prompt=prompt, params=parameters)
        return response["results"][0]["generated_text"]
