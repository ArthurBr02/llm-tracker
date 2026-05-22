## LLM-Tracker

LLM-Tracker is a Python script that tracks the availability of new Large Language Models (LLMs) across multiple platforms and sends an email notification when new models are added.

Currently supported platforms:
- **OpenRouter**
- **Ollama**
- **LM Studio**

## How it works

The script fetches the available models from each platform's API or webpage and compares them against a local cache stored in the `data/` directory (`openrouter.json`, `ollama.json`, `lmstudio.json`). If new models or new versions are detected, it updates the local cache and sends you an email summary with the new models' details.

## Installation

1. Install dependencies:
```bash
pip3 install -r requirements.txt
```

2. Configure environment variables by copying `env.example` to `.env`:
```bash
cp env.example .env
```

3. Edit `.env` with your SMTP configuration (and API keys):
```text
EMAIL_FROM=your-email@example.com
EMAIL_TO=recipient@example.com
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USERNAME=your-username
EMAIL_PASSWORD=your-password

MISTRAL_API_KEY=your-api-key # Used for the experimental Mistral parser
```

## Usage

Run the script:
```bash
python3 main.py
```

This will fetch all available models from the configured providers and send an email alert summarizing any new models discovered.


