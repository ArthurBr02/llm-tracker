import requests
import os
import smtplib
from email.mime.text import MIMEText

from file import init_data_file
from file import save_model_to_file

from dotenv import load_dotenv

load_dotenv()

OPENROUTER_URL = "https://openrouter.ai/api/v1/models"
DATA_FILE_NAME = "openrouter.json"
DATA_DIR = "data"

data = None
filename = None

def get_models():
    API_KEY = os.getenv('OPENROUTER_API_KEY')
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(OPENROUTER_URL, headers=headers)
    if response.status_code == 200:
        return response.json().get('data', [])
    else:
        print(f"Failed to fetch models: {response.status_code}")
        return None

def send_email_notification(new_models):
    FROM = os.getenv('EMAIL_FROM')
    TO = [email.strip() for email in (os.getenv('EMAIL_TO') or "").split(",") if email.strip()]
    HOST = os.getenv('EMAIL_HOST')
    PORT = os.getenv('EMAIL_PORT')
    USERNAME = os.getenv('EMAIL_USERNAME')
    PASSWORD = os.getenv('EMAIL_PASSWORD')
    SUBJECT = "Openrouter - New Models Added"
    BODY = "The following new models have been added:\n\n"
    
    models_info = []

    for model in new_models:
        model_info = f"- {model['name']} (ID: {model['id']})\n"

        architecture = model.get('architecture') or {}
        input = architecture.get('input_modalities') or "N/A"
        output = architecture.get('output_modalities') or "N/A"
        pricing = model.get('pricing') or {}
        date = model.get('created') or "N/A"

        model_info += f"  Input Modalities: {', '.join(input) if isinstance(input, list) else input}\n"
        model_info += f"  Output Modalities: {', '.join(output) if isinstance(output, list) else output}\n"
        model_info += f"  Context length: {model.get('context_length', 'N/A')}\n"
        model_info += f"  Created: {date}\n"

        is_free = all(float(v or 0) == 0 for v in pricing.values()) if pricing else False
        model_info += f"  Free: {is_free}\n"

        if not is_free:
            model_info += f"  Pricing\n"

            for sku, price in pricing.items():
                model_info += f"    - {sku}: {price}\n"

        model_info += f"  URL: https://openrouter.ai/models/{model['id']}\n\n"

        models_info.append(model_info)

    BODY += "----------------------------------\n".join(models_info)
    msg = MIMEText(BODY)
    msg['Subject'] = SUBJECT
    msg['From'] = FROM
    msg['To'] = ", ".join(TO)

    s = smtplib.SMTP(HOST, PORT)
    s.starttls()
    s.login(USERNAME, PASSWORD)
    s.sendmail(FROM, TO, msg.as_string())
    s.quit()

def execute():
    models = get_models()
    data, filename = init_data_file(DATA_DIR, DATA_FILE_NAME)

    new_models = []

    if models:
        print("Available Models ({}):".format(len(models)))
        for model in models:
            print(f"- {model['name']} (ID: {model['id']})")

            id = f"{model['canonical_slug']}_{model['created']}"

            if id not in data:
                save_model_to_file(data, filename, model, id)
                new_models.append(model)
            else:
                print("Model already exists.")

    # Notification
    if new_models:
        print("\nNew models added:")
        for model in new_models:
            print(f"- {model['name']} (ID: {model['id']})")
        send_email_notification(new_models)
    else:
        print("\nNo new models were added.")