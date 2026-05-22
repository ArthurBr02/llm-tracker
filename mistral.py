import os
from mistralai.client import Mistral

from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")
model = "mistral-medium-latest"

def parse_models(prompt_system_filename, content):
    prompt_system = None
    with open(prompt_system_filename, 'r') as f:
        prompt_system = f.read()

    client = Mistral(
        api_key=api_key,
        timeout_ms=600000  # 10 minutes
    )

    print("Sending content to Mistral for parsing...")
    chat_response = client.chat.complete(
        model = model,
        messages = [
            {
                "role": "system",
                "content": prompt_system,
            },
            {
                "role": "user",
                "content": "Voici mon contenu: " + content,
            }
        ]
    )
    print("Received response from Mistral.")

    return chat_response.choices[0].message.content.strip()