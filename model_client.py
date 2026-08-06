import os
import time

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Read API key and model name from .env
api_key = os.getenv("OPENROUTER_API_KEY")
model_name = os.getenv("OPENROUTER_MODEL")

# Create OpenRouter client
client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)


def generate_response(prompt):
    # Start timer
    start_time = time.time()

    # Send request to OpenRouter
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # End timer
    end_time = time.time()
    latency = end_time - start_time

    print(response)

     # Return response with metadata
    return {
        "text": response.choices[0].message.content,
        "model": model_name,
        "latency": latency
    }