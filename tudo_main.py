# requirements: requests, beautifulsoup4, python-dotenv, twilio (if SMS)
import os
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import smtplib

load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
MAIL_EMAIL = os.getenv("mail_email")
MAIL_PASSWORD = os.getenv("mail_password")  # use app password

# TW_SID = os.getenv("account_sid")
# TW_TOKEN = os.getenv("auth_token")
TW_FROM = "+13516664633"
TW_TO = "+905537497743"

URL = "https://www.stwdo.de/wohnen/aktuelle-wohnangebote"
sad_text = (
    "Schade - leider haben wir aktuell keine freien Plätze zu vermieten! "
    "Bitte schauen Sie zu einem späteren Zeitpunkt noch einmal hier vorbei."
)

def send_email(msg):
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=60) as s:
        s.starttls()
        s.login(MAIL_EMAIL, MAIL_PASSWORD)
        s.sendmail(MAIL_EMAIL, [MAIL_EMAIL], f"Subject:TU-Dortmund\n\n{msg}")

# def send_sms(body):
#     if not TW_SID or not TW_TOKEN:
#         return
#     client = Client(TW_SID, TW_TOKEN)
#     client.messages.create(from_=TW_FROM, to=TW_TO, body=body)

def check_site():
    try:
        r = requests.get(URL, timeout=20, headers={"User-Agent":"Mozilla/5.0"})
        r.raise_for_status()
    except Exception as e:
        send_email("Error fetching page: " + str(e))
        return False

    soup = BeautifulSoup(r.text, "html.parser")
    # try to find notifications
    notifications = soup.select(".notification__body")
    texts = [n.get_text(strip=True) for n in notifications]
    # fallback: search whole page text
    page_text = r.text

    # if sad_text present in any notification or page, then no offer
    for t in texts:
        if sad_text in t:
            return True
    if sad_text in page_text:
        return True

    # if we reach here, likely there is an offer
    return False

if __name__ == "__main__":
    has_no_offer = check_site()
    if not has_no_offer:
        send_email("There is a room at TU dortmund")
        # send_sms("There is a room at TU dortmund")
    else:
        # send_email("There is a room at TU dortmund")
        # send_sms("There is a room at TU dortmund")
        print("nichts")
        pass
