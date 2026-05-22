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
        # i = 0
        # while True and i < 5:
        #     try:
        #         models = parse_models(content)
        #         json_models = json.loads(models)
        #         return json_models
        #     except Exception as e:
        #         print(f"Error parsing models: {e}")
        #         print(f"{i}/5 - Retrying...")
        #         i += 1
        
        # if i == 5:
        #     print("Failed to parse models after 5 attempts.")
        #     return None
        return parse_models_2(content)
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

def parse_models_2(model):
    soup = bs4.BeautifulSoup(str(model), 'html.parser')
    cards = soup.select('a[href^="/models/"]')
    if not cards and soup.name == 'a':
        cards = [soup]

    models = []

    for card in cards:
        name_tag = card.select_one('.text-lg.font-medium')
        name = name_tag.get_text(strip=True) if name_tag else card.get('title')
        if not name:
            continue

        href = card.get('href')
        if href and href.startswith('/models/'):
            slug = href.split('/models/', 1)[1].strip('/')
            url = f"https://lmstudio.ai/models/{slug}" if slug else href
        else:
            url = href

        description_tag = card.select_one('.text-muted-foreground')
        description = description_tag.get_text(" ", strip=True) if description_tag else None

        sizes = []
        for size_tag in card.select('[title^="Model size:"]'):
            size = size_tag.get_text(strip=True)
            if size and size not in sizes:
                sizes.append(size)

        text_content = card.get_text(" ", strip=True).lower()
        capabilities = {
            "tools": True if any(keyword in text_content for keyword in ["tool calling", "tool use", "tool", "function calling", "function-calling"]) else None,
            "reasoning": True if any(keyword in text_content for keyword in ["reasoning", "thinking"]) else None,
            "vision": True if any(keyword in text_content for keyword in ["vision", "image", "multimodal"]) else None,
        }

        stats = card.select('span.font-medium')
        downloads_tag = stats[0] if len(stats) > 0 else None
        likes_tag = stats[1] if len(stats) > 1 else None

        downloads = downloads_tag.get_text(strip=True) if downloads_tag else None
        likes_text = likes_tag.get_text(strip=True) if likes_tag else None
        likes = int(likes_text) if likes_text and likes_text.isdigit() else likes_text

        updated = None
        for element in card.select('[class*="opacity-70"]'):
            element_text = element.get_text(" ", strip=True)
            if element_text.lower().startswith('updated '):
                updated = element_text.replace('Updated ', '', 1)
                break
        if not updated:
            updated = "Unknown"

        models.append({
            "name": name,
            "url": url,
            "description": description,
            "sizes": sizes,
            "capabilities": capabilities,
            "downloads": downloads,
            "likes": likes,
            "updated": updated,
        })

    return models

def send_email_notification(new_models):
    FROM = os.getenv('EMAIL_FROM')
    TO = os.getenv('EMAIL_TO')
    HOST = os.getenv('EMAIL_HOST')
    PORT = os.getenv('EMAIL_PORT')
    USERNAME = os.getenv('EMAIL_USERNAME')
    PASSWORD = os.getenv('EMAIL_PASSWORD')
    SUBJECT = "LMStudio - New Models Added"
    BODY = "The following new models have been added:\n\n"

    models_info = []

    for model in new_models:
        model_info = f"- {model['name']}\n"

        capabilities = model.get('capabilities') or "N/A"

        _capabilities = []
        for capability, value in capabilities.items():
            if value is True:
                _capabilities.append(capability.capitalize())

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