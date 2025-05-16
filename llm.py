import json
import os
from typing import Any
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read the bearer token from the environment
bearer_token = os.getenv("BEARER_TOKEN")

# Validate it's loaded
if not bearer_token:
    raise ValueError("❌ BEARER_TOKEN is not set in the environment!")

# Define headers
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {bearer_token}'
}

URL = "https://api.asi1.ai/v1/chat/completions"
 
MODEL = "asi1-mini"
 
 
async def get_completion(context: str,prompt: str,) -> str:
    payload = json.dumps({
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": context + " " + prompt
            }
        ],
        "temperature": 0,
        "stream": False,
        "max_tokens": 0
    })
 
    response = requests.request("POST", URL, headers=HEADERS, data=payload)
 
    return response.json()
 
 
 