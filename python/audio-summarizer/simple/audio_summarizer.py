import os
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import Credentials
from dotenv import load_dotenv

load_dotenv()


def generate_summary(text):
    # Load Watsonx Credentials
    credentials = Credentials(
        api_key=os.getenv("WATSONX_APIKEY"), url=os.getenv("WATSONX_URL")
    )
    model_id = "meta-llama/llama-3-3-70b-instruct"
    project_id = os.getenv("WATSONX_PROJECT_ID")
    llm = ModelInference(
        model_id=model_id, credentials=credentials, project_id=project_id
    )

    prompt = f"""### 🎯 Prompt: Summarize Transcript

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

    response = llm.generate(prompt=prompt, params=parameters)
    return_data = response["results"][0]["generated_text"]
    return return_data


def speech_to_text(audio_path, mime_type):
    try:
        authenticator = IAMAuthenticator(os.getenv("WATSONX_S2T_APIKEY"))
        speech_to_text = SpeechToTextV1(authenticator=authenticator)
        speech_to_text.set_service_url(os.getenv("WATSONX_S2T_URL"))

        with open(
            audio_path,
            "rb",
        ) as audio_file:
            speech_recognition_results = speech_to_text.recognize(
                audio=audio_file, content_type=mime_type
            ).get_result()

        transcript = " ".join(
            [
                result["alternatives"][0]["transcript"].strip()
                for result in speech_recognition_results["results"]
            ]
        )
        return transcript
    except Exception as e:
        return str(e)


def audio_summarizer(audio_file_path, mime_type):
    audio_text = speech_to_text(audio_file_path, mime_type)
    print("-" * 75)
    print("AUDIO TEXT")
    print("-" * 75)
    print(audio_text)
    print("-" * 75)
    audio_summary = generate_summary(audio_text)
    print("AUDIO SUMMARY")
    print("-" * 75)
    print(audio_summary)
    return audio_summary


if __name__ == "__main__":
    audio_file_path = "./2025_IBM_Quantum_Roadmap_update.mp3"
    audio_summary = audio_summarizer(audio_file_path, "audio/mpeg")
