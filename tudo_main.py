import os
import smtplib
from dotenv import load_dotenv
from twilio.rest import Client
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

load_dotenv()


# Mail
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_timeout = 60  # Increase timeout to 60 seconds

mail_email = os.getenv("mail_email")
mail_password = os.getenv("mail_password")
message_positive= "There is a room at TU dortmund"
message_negative= "There is something wrong with the website"

def send_email(msg):
    with smtplib.SMTP(smtp_server, smtp_port, timeout=smtp_timeout) as connection:
        connection.starttls()
        connection.login(user=mail_email, password=mail_password)
        connection.sendmail(
            from_addr=mail_email,
            to_addrs="kadirarslan917@gmail.com",
            msg=f"Subject:TU-Dortmund\n\n{msg}"
        )


def send_sms():
    account_sid = os.getenv("account_sid")
    auth_token = os.getenv("auth_token")
    client = Client(account_sid, auth_token)
    client.messages.create(
        from_="+13516664633",
        body=message_positive,
        to='+905537497743'
    )


options = Options()
options.add_argument("--headless")  # run in background without opening a window
driver = webdriver.Chrome(options=options)

# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_experimental_option("detach", True)
# driver = webdriver.Chrome(options=chrome_options)

driver.get("https://www.stwdo.de/wohnen/aktuelle-wohnangebote")

# Find the button and click
search_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "input.button.is-primary[type='submit']"))
)
search_button.click()


sad_text = (
    "Schade - leider haben wir aktuell keine freien Plätze zu vermieten! "
    "Bitte schauen Sie zu einem späteren Zeitpunkt noch einmal hier vorbei."
)


def no_offer():
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'notification__body'))
        )
        bodies = driver.find_elements(By.CLASS_NAME, 'notification__body')
        texts = [b.text for b in bodies]
    except TimeoutException:
        send_email(message_negative)
        return True
    except Exception as e:
        print(f"Selenium error in no_offer: {e}")
        return True

    for text in texts:
        if sad_text in text:
            return True
    return False

try:
    if not no_offer():
        send_email(message_positive)
        send_sms()
    else:
        print("the code works")
except Exception as e:
    print(f"Selenium error in no_offer: {e}")
finally:
    driver.quit()
