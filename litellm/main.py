import json
import os
from dotenv import load_dotenv

load_dotenv()
from litellm import completion, transcription

os.environ["WATSONX_URL"] = os.getenv("WATSONX_URL")
os.environ["WATSONX_APIKEY"] = os.getenv("WATSONX_APIKEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")


audio_file = open("WelcometoGroqConsole.mp4", "rb")

transcript = transcription(
    model="groq/whisper-large-v3",
    file=audio_file,
    prompt="Specify context or spelling",
    temperature=0,
    response_format="json",
)

transcript = transcript["text"]

print("---------------Transcript---------------")
print(transcript)

print("---------------Summary---------------")
response = completion(
    model="watsonx/meta-llama/llama-3-3-70b-instruct",
    messages=[
        {
            "role": "system",
            "content": "You are an expert meeting summarizer. Provide clear, structured, and concise summaries.",
        },
        {
            "role": "user",
            "content": f"""
Summarize the following transcript.

Requirements:
- Provide a concise executive summary (5-8 lines)
- List key discussion points
- List action items (if any)
- Maintain clarity and professional tone

Transcript:
{transcript}
""",
        },
    ],
    temperature=0.3,
    max_tokens=800,
    project_id=os.getenv("WATSONX_PROJECT_ID"),
)

print(response["choices"][0]["message"]["content"])
print("---------------Usage---------------")
print(response["usage"])
