import requests
import os
import bs4
import smtplib
from email.mime.text import MIMEText
import json

from file import init_data_file
from file import save_model_to_file

import mistral

from dotenv import load_dotenv

load_dotenv()

LMSTUDIO_URL="https://lmstudio.ai/models"
DATA_FILE_NAME = "lmstudio.json"
DATA_DIR = "data"
PROMPT_SYSTEM_FILENAME = "prompt-system-lmstudio.txt"

def get_models():
    response = requests.get(LMSTUDIO_URL)
    if response.status_code == 200:
        content = response.text
        i = 0
        while True and i < 5:
            try:
                models = parse_models(content)
                json_models = json.loads(models)
                return json_models
            except Exception as e:
                print(f"Error parsing models: {e}")
                print(f"{i}/5 - Retrying...")
                i += 1
        
        if i == 5:
            print("Failed to parse models after 5 attempts.")
            return None
    else:
        print(f"Failed to fetch models: {response.status_code}")
        return None

def parse_models(content):
    soup = bs4.BeautifulSoup(content, 'html.parser')
    models = []
    a = soup.select('div.grid a[href^="/models/"]')
    print(len(a))
    for link in a:
        href = link.get('href')
        if href and href.startswith("/models/"):
            models.append(link)
    
    return mistral.parse_models(PROMPT_SYSTEM_FILENAME, str(models))

def send_email_notification(new_models):
    FROM = os.getenv('EMAIL_FROM')
    TO = os.getenv('EMAIL_TO')
    HOST = os.getenv('EMAIL_HOST')
    PORT = os.getenv('EMAIL_PORT')
    USERNAME = os.getenv('EMAIL_USERNAME')
    PASSWORD = os.getenv('EMAIL_PASSWORD')
    SUBJECT = "LMStudio - New Models Added"
    BODY = "The following new models have been added:\n\n"
    
    # [
    # {
    #     "name": "Granite 4.1",
    #     "url": "https://huggingface.co/models/granite-4.1",
    #     "description": "Granite 4.1 models are new and improved granite models which have gone through an improved post-training pipeline, including supervised finetuning and reinforcement learning alignment, resulting in enhanced tool calling, instruction following, and chat capabilities.",
    #     "sizes": ["3B", "8B", "30B"],
    #     "capabilities": {
    #     "tools": true,
    #     "reasoning": null,
    #     "vision": null
    #     },
    #     "downloads": "1.6K",
    #     "likes": 1,
    #     "updated": "1 day ago"
    # }
    # ]

    models_info = []

    for model in new_models:
        model_info = f"- {model['name']}\n"

        capabilities = model.get('capabilities') or "N/A"

        _capabilities = []
        for capability, value in capabilities.items():
            if value is True:
                _capabilities.append(capability.capitalize())
            elif value is not None:
                _capabilities.append(f"{capability.capitalize()}: {value}")

        sizes = model.get('sizes') or "N/A"
        downloads = model.get('downloads') or "N/A"
        likes = model.get('likes') or "N/A"

        date = model.get('updated') or "N/A"
        
        model_info += f"  Capabilities: {', '.join(_capabilities) if isinstance(_capabilities, list) else _capabilities}\n"
        model_info += f"  Sizes: {', '.join(sizes) if isinstance(sizes, list) else sizes}\n"
        model_info += f"  Downloads: {downloads}\n"
        model_info += f"  Likes: {likes}\n"
        model_info += f"  Last Updated: {date}\n"

        model_info += f"  URL: {model['url']}\n\n"
        
        models_info.append(model_info)

    BODY += "----------------------------------\n".join(models_info)
    msg = MIMEText(BODY)
    msg['Subject'] = SUBJECT
    msg['From'] = FROM
    msg['To'] = TO

    s = smtplib.SMTP(HOST, PORT)
    s.starttls()
    s.login(USERNAME, PASSWORD)
    s.sendmail(FROM, [TO], msg.as_string())
    s.quit()


def execute():
    models = get_models()
    data, filename = init_data_file(DATA_DIR, DATA_FILE_NAME)

    new_models = []

    if models:
        print("Available Models ({}):".format(len(models)))
        for model in models:
            print(f"- {model['name']} (ID: {model['name']}_{model['updated']})")

            id = model['name'] + "_" + model['updated']
            if id not in data:
                save_model_to_file(data, filename, model, id)
                new_models.append(model)
            else:
                print("Model already exists.")

    # Notification
    if new_models:
        print("\nNew models added:")
        for model in new_models:
            print(f"- {model['name']} (ID: {model['name']}_{model['updated']})")
        send_email_notification(new_models)
    else:
        print("\nNo new models were added.")

if __name__ == "__main__":
    execute()