import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()


def audio_translation(file_path):
    """Ask user input and send it to Groq model."""
    # Initialize Groq client
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    result = ""
    # Open the audio file
    with open(file_path, "rb") as file:
        # Create a translation of the audio file
        translation = client.audio.translations.create(
            file=(file_path, file.read()),  # Required audio file
            model="whisper-large-v3",  # Required model to use for translation
            prompt="Specify context or spelling",  # Optional
            response_format="json",  # Optional
            temperature=0.0,  # Optional
        )
        result = translation.text

    print("\n" + "-" * 50)
    print("RESULT")
    print("-" * 50)
    print(result)


# Run the function
if __name__ == "__main__":
    file_path = os.path.dirname(__file__) + "/WelcometoGroqConsole.mp4"
    audio_translation(file_path)
