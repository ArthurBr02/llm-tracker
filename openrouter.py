import requests
import os
import smtplib
from email.mime.text import MIMEText

from file import init_data_file
from file import save_model_to_file

from dotenv import load_dotenv

load_dotenv()

OPENROUTER_URL = "https://openrouter.ai/api/frontend/models"
DATA_FILE_NAME = "openrouter.json"
DATA_DIR = "data"

data = None
filename = None

def get_models():
    response = requests.get(OPENROUTER_URL)
    if response.status_code == 200:
        return response.json().get('data', [])
    else:
        print(f"Failed to fetch models: {response.status_code}")
        return None

def send_email_notification(new_models):
    FROM = os.getenv('EMAIL_FROM')
    TO = os.getenv('EMAIL_TO')
    HOST = os.getenv('EMAIL_HOST')
    PORT = os.getenv('EMAIL_PORT')
    USERNAME = os.getenv('EMAIL_USERNAME')
    PASSWORD = os.getenv('EMAIL_PASSWORD')
    SUBJECT = "Openrouter - New Models Added"
    BODY = "The following new models have been added:\n\n"
    
    models_info = []

    for model in new_models:
        model_info = f"- {model['name']} (ID: {model['permaslug']})\n"

        input = model.get('input_modalities') or "N/A"
        output = model.get('output_modalities') or "N/A"
        endpoint = model.get('endpoint') or {}
        date = model.get('created_at') or "N/A"
        
        model_info += f"  Input Modalities: {', '.join(input) if isinstance(input, list) else input}\n"
        model_info += f"  Output Modalities: {', '.join(output) if isinstance(output, list) else output}\n"
        model_info += f"  Context length: {endpoint.get('context_length', 'N/A')}\n"
        model_info += f"  Free: {endpoint.get('is_free', 'N/A')}\n"
        model_info += f"  Created At: {date}\n"

        if not endpoint.get('is_free', False):
            model_info += f"  Pricing\n"

            for display_pricing in endpoint.get('display_pricing', []):
                display_pricing = display_pricing or {}
                model_info += f"    - {display_pricing.get('sku_label', 'N/A')}: {display_pricing.get('price', 'N/A')}{display_pricing.get('unitLabel', 'N/A') }\n"

        model_info += f"  Quantization: {model.get('quantization', 'N/A')}\n"
        model_info += f"  URL: https://openrouter.ai/models/{model['permaslug']}\n\n"
        
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
            print(f"- {model['name']} (ID: {model['permaslug']})")

            endpoint = model.get('endpoint') or {}
            is_free = endpoint.get('is_free', False)
            free_info = "Free" if is_free else "Paid"
            id = model['permaslug'] + "_" + free_info

            if id not in data:
                save_model_to_file(data, filename, model, id)
                new_models.append(model)
            else:
                print("Model already exists.")

    # Notification
    if new_models:
        print("\nNew models added:")
        for model in new_models:
            print(f"- {model['name']} (ID: {model['permaslug']})")
        send_email_notification(new_models)
    else:
        print("\nNo new models were added.")