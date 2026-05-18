import requests
import json
import os
import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText

OPENROUTER_URL = "https://openrouter.ai/api/frontend/models"
DATA_FILE_NAME = "models.json"
DATA_DIR = "data"

load_dotenv()

data = None
filename = None

def get_models():
    response = requests.get(OPENROUTER_URL)
    if response.status_code == 200:
        return response.json().get('data', [])
    else:
        print(f"Failed to fetch models: {response.status_code}")
        return None

def init_data_file():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    filename = f"{DATA_DIR}/{DATA_FILE_NAME}"
    
    # Create file if it doesn't exist
    if not os.path.isfile(filename):
        with open(filename, 'w') as f:
            json.dump({}, f)
    
    # Read existing data
    data = {}
    with open(filename, 'r') as f:
        content = f.read()
        data = json.loads(content) if content else {}

    return data, filename

def save_model_to_file(model):
    global data, filename

    # Ajouter le nouveau modèle
    data[model['permaslug']] = model
    
    # Écrire le tout
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def send_email_notification(new_models):
    FROM = os.getenv('EMAIL_FROM')
    TO = os.getenv('EMAIL_TO')
    HOST = os.getenv('EMAIL_HOST')
    PORT = os.getenv('EMAIL_PORT')
    USERNAME = os.getenv('EMAIL_USERNAME')
    PASSWORD = os.getenv('EMAIL_PASSWORD')
    SUBJECT = "New Models Added"
    BODY = "The following new models have been added:\n\n"
    
    models_info = []

    for model in new_models:
        model_info = f"- {model['name']} (ID: {model['permaslug']})\n"

        input = model.get('input_modalities', "N/A")
        output = model.get('output_modalities', "N/A")
        endpoint = model.get('endpoint', {})
        date = model.get('created_at', "N/A")
        
        model_info += f"  Input Modalities: {', '.join(input) if isinstance(input, list) else input}\n"
        model_info += f"  Output Modalities: {', '.join(output) if isinstance(output, list) else output}\n"
        model_info += f"  Context length: {endpoint.get('context_length', 'N/A')}\n"
        model_info += f"  Free: {endpoint.get('is_free', 'N/A')}\n"
        model_info += f"  Created At: {date}\n"

        if not endpoint.get('is_free', False):
            model_info += f"  Pricing\n"

            for display_pricing in endpoint.get('display_pricing', []):
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

if __name__ == "__main__":
    models = get_models()
    data, filename = init_data_file()

    new_models = []

    if models:
        print("Available Models ({}):".format(len(models)))
        for model in models:
            print(f"- {model['name']} (ID: {model['permaslug']})")
            if model['permaslug'] not in data:
                save_model_to_file(model)
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