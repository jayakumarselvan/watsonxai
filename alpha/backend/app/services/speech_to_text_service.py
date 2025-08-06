import os
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from dotenv import load_dotenv

from app import constant

load_dotenv()


class SpeechToTextService:
    def __init__(self):
        authenticator = IAMAuthenticator(constant.WATSONX_S2T_APIKEY)
        self.s2t = SpeechToTextV1(authenticator=authenticator)
        self.s2t.set_service_url(constant.WATSONX_S2T_URL)

    def transcribe(self, audio_path: str, mime_type: str) -> str:
        with open(audio_path, "rb") as audio_file:
            result = self.s2t.recognize(
                audio=audio_file, content_type=mime_type
            ).get_result()

        transcript = " ".join(
            [r["alternatives"][0]["transcript"].strip() for r in result["results"]]
        )
        return transcript
