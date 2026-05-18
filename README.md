## LLM-Tracker

LLM-Tracker is a script sending an email containing all the new models available on Openrouter.

## Installation

1. Install dependencies:
```bash
pip3 install -r requirements.txt
```

2. Configure environment variables by copying `env.example` to `.env`:
```bash
cp env.example .env
```

3. Edit `.env` with your SMTP configuration:
```
EMAIL_FROM=your-email@example.com
EMAIL_TO=recipient@example.com
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USERNAME=your-username
EMAIL_PASSWORD=your-password
```

## Usage

Run the script:
```bash
python3 main.py
```

This will fetch all available models from OpenRouter and send an email with new models.

