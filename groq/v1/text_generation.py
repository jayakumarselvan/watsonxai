import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()


def ask_groq(user_input):
    """Ask user input and send it to Groq model."""
    # Initialize Groq client
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    # Send request to model
    chat_completion = client.chat.completions.create(
        messages=[
            # Set an optional system message. This sets the behavior of the
            # assistant and can be used to provide specific instructions for
            # how it should behave throughout the conversation.
            {"role": "system", "content": "You are a helpful assistant."},
            # Set a user message for the assistant to respond to.
            {
                "role": "user",
                "content": user_input,
            },
        ],
        # The language model which will generate the completion.
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
    # Ask user for input
    user_input = input("Enter your question or prompt for the model: ")
    ask_groq(user_input)
