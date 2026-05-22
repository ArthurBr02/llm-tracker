import requests
import os
import bs4
import smtplib
from email.mime.text import MIMEText

from file import init_data_file
from file import save_model_to_file

from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL="https://ollama.com/library?sort=newest"
DATA_FILE_NAME = "ollama.json"
DATA_DIR = "data"

def get_models():
    response = requests.get(OLLAMA_URL)
    if response.status_code == 200:
        content = response.text
        soup = bs4.BeautifulSoup(content, 'html.parser')
        models = []
        for model in soup.select('.grid > li.items-baseline'):
            models.append(parse_model(model))
        return models
    else:
        print(f"Failed to fetch models: {response.status_code}")
        return None

def parse_model(model):
    name = model.select_one('a > div > h2').text.strip()


    capabilities = []
    sizes = []
    spans = model.select('a > div > div > span')
    for span in spans:
        if span.attrs.get('x-test-capability') is not None:
            capabilities.append(span.text.strip())
        elif span.attrs.get('x-test-size') is not None:
            sizes.append(span.text.strip())


    pulls = "0"
    tags = 0

    spans = model.select('a > div > p > span > span')
    for span in spans:        
        if span.attrs.get('x-test-pull-count') is not None:
            pulls = span.text.strip()
        if span.attrs.get('x-test-tag-count') is not None:
            tags = span.text.strip()

    last_updated = "Unknown"
    spans = model.select('a > div > p > span')
    for span in spans:
        if span.attrs.get('title') is not None:
            last_updated = span.attrs.get('title').strip()

    return {
        'name': name,
        'capabilities': capabilities,
        'sizes': sizes,
        'pulls': pulls,
        'tags': tags,
        'last_updated': last_updated
    }

def send_email_notification(new_models):
    FROM = os.getenv('EMAIL_FROM')
    TO = os.getenv('EMAIL_TO')
    HOST = os.getenv('EMAIL_HOST')
    PORT = os.getenv('EMAIL_PORT')
    USERNAME = os.getenv('EMAIL_USERNAME')
    PASSWORD = os.getenv('EMAIL_PASSWORD')
    SUBJECT = "Ollama - New Models Added"
    BODY = "The following new models have been added:\n\n"
    
    models_info = []

    for model in new_models:
        model_info = f"- {model['name']}\n"

        capabilities = model.get('capabilities') or "N/A"
        sizes = model.get('sizes') or "N/A"
        pulls = model.get('pulls') or "N/A"
        tags = model.get('tags') or "N/A"

        date = model.get('last_updated') or "N/A"
        
        model_info += f"  Capabilities: {', '.join(capabilities) if isinstance(capabilities, list) else capabilities}\n"
        model_info += f"  Sizes: {', '.join(sizes) if isinstance(sizes, list) else sizes}\n"
        model_info += f"  Pulls: {pulls}\n"
        model_info += f"  Tags: {tags}\n"
        model_info += f"  Last Updated: {date}\n"

        model_info += f"  URL: https://ollama.com/library/{model['name']}\n\n"
        
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
            print(f"- {model['name']} (ID: {model['name']}_{model['last_updated']})")

            id = model['name'] + "_" + model['last_updated']
            if id not in data:
                save_model_to_file(data, filename, model, id)
                new_models.append(model)
            else:
                print("Model already exists.")

    # Notification
    if new_models:
        print("\nNew models added:")
        for model in new_models:
            print(f"- {model['name']} (ID: {model['name']}_{model['last_updated']})")
        send_email_notification(new_models)
    else:
        print("\nNo new models were added.")

if __name__ == "__main__":
    execute()