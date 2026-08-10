import os
import time
import json
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Read OpenRouter API key and model name from .env
api_key = os.getenv("OPENROUTER_API_KEY")
model_name = os.getenv("OPENROUTER_MODEL")

# Create OpenRouter client
client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)


def log_model_failure(error_message):

    log_file = os.path.join("logs", "model_failures.json")

    os.makedirs("logs", exist_ok=True)

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "failure_type": "model_error",
        "reason": error_message
    }

    try:
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as file:
                logs = json.load(file)

                if not isinstance(logs, list):
                    logs = []
        else:
            logs = []

    except (json.JSONDecodeError, FileNotFoundError):
        logs = []

    logs.append(log_entry)

    with open(log_file, "w", encoding="utf-8") as file:
        json.dump(logs, file, indent=4)


def generate_response(prompt):

    # Start timer
    start_time = time.time()

    try:
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

    except Exception as e:

        # Record model/network failure
        log_model_failure(str(e))

        return {
            "text": None,
            "model": model_name,
            "latency": time.time() - start_time,
            "error": str(e)
        }

    # End timer
    end_time = time.time()
    latency = end_time - start_time

    print(response)

    # Return successful response with metadata
    return {
        "text": response.choices[0].message.content,
        "model": model_name,
        "latency": latency
    }