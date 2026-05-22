import smtplib
from email.mime.text import MIMEText
import os

from dotenv import load_dotenv

load_dotenv()

def send_error_notification(subject, error_message):
    FROM = os.getenv('EMAIL_FROM')
    TO = os.getenv('EMAIL_TO')
    HOST = os.getenv('EMAIL_HOST')
    PORT = os.getenv('EMAIL_PORT')
    USERNAME = os.getenv('EMAIL_USERNAME')
    PASSWORD = os.getenv('EMAIL_PASSWORD')

    msg = MIMEText(f"An error occurred during execution:\n\n{error_message}")
    msg['Subject'] = subject
    msg['From'] = FROM
    msg['To'] = TO

    try:
        with smtplib.SMTP(HOST, PORT) as server:
            server.starttls()
            server.login(USERNAME, PASSWORD)
            server.sendmail(FROM, TO, msg.as_string())
        print("Error notification sent successfully.")
    except Exception as e:
        print(f"Failed to send error notification: {e}")