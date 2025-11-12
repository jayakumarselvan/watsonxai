import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()


def ask_groq():
    """Ask user input and send it to Groq model."""
    # Initialize Groq client
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    # Ask user for input
    user_input = input("Enter your question or prompt for the model: ")

    # Send request to model
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": user_input}],
        model="llama-3.3-70b-versatile",
    )

    # Extract and print result
    result = chat_completion.choices[0].message.content
    print("\n" + "-" * 50)
    print("RESULT")
    print("-" * 50)
    print(result)


# Run the function
if __name__ == "__main__":
    ask_groq()
