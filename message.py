import os
import utils
import requests
import dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

dotenv.load_dotenv(dotenv_path="./.env")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", default=None)
TELEGRAM_BOT_URL = os.getenv(
    "TELEGRAM_BOT_URL", default="https://api.telegram.org/"
)
TELEGRAM_BOT_CHAT_ID = os.getenv("TELEGRAM_BOT_CHAT_ID")

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER")
EMAIL_SMTP_PORT = os.getenv("EMAIL_SMTP_PORT")
EMAIL_SMTP_USERNAME = os.getenv("EMAIL_SMTP_USERNAME")
EMAIL_SMTP_PASSWORD = os.getenv("EMAIL_SMTP_PASSWORD")


def send_telegram_message(message: str) -> bool:
    if utils.is_any_null_or_empty(TELEGRAM_BOT_TOKEN, TELEGRAM_BOT_CHAT_ID):
        return False

    try:
        requests.post(
            f"{TELEGRAM_BOT_URL}bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data={
                "chat_id": TELEGRAM_BOT_CHAT_ID,
                "text": message,
                "parse_mode": "HTML",
            },
        )
        return True
    except Exception:
        return False


def send_email_smtp(subject: str, body: str) -> False:
    if utils.is_any_null_or_empty(
        EMAIL_FROM,
        EMAIL_TO,
        EMAIL_SMTP_SERVER,
        EMAIL_SMTP_PORT,
        EMAIL_SMTP_USERNAME,
        EMAIL_SMTP_PASSWORD,
    ):
        return False

    message = MIMEMultipart()
    message["From"] = EMAIL_FROM
    message["To"] = EMAIL_TO
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL(
            EMAIL_SMTP_SERVER, int(EMAIL_SMTP_PORT)
        ) as server:
            server.login(EMAIL_SMTP_USERNAME, EMAIL_SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, message.as_string())
        return True
    except smtplib.SMTPException:
        return False
