from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pytesseract
from PIL import Image
from bs4 import BeautifulSoup
import requests
import io
import email
from email.message import EmailMessage
import smtplib
from dotenv import load_dotenv
import os


# https://stackoverflow.com/a/61157968
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)


driver.get("https://zuerich.migros.ch/de/outlet-migros.html")
content = driver.page_source
soup = BeautifulSoup(content)


def extract_text(img):
    base_url = 'https://zuerich.migros.ch'
    image_url = base_url + img['src']
    # replace 'small' with 'large' in URL
    image_url_big = image_url.replace('small', 'large', 1)

    image_content = requests.get(image_url_big).content
    image_file = io.BytesIO(image_content)

    # Extract the text from the image
    image = Image.open(image_file)
    # Perform OCR using PyTesseract
    text = pytesseract.image_to_string(image)
    return text

def send_success_mail(img_text: str):
    sender = os.environ['SENDER']
    recipient = os.environ['RECEIPIENT']
    password = os.environ['PASSWORD']

    email = EmailMessage()
    email["From"] = sender
    email["To"] = recipient
    email["Subject"] = 'M-Outlet Notifier'
    email.set_content(img_text)

    smtp = smtplib.SMTP("smtp.office365.com", port=587)
    smtp.starttls()
    smtp.login(sender, password)
    smtp.sendmail(sender, recipient, email.as_string())
    smtp.quit()

if __name__ == "__main__":
    load_dotenv()
    # images = soup.find_all(attrs={'class': 'image lazyloaded'})
    max_tries = 5
    t_count = 0
    success = False

    while t_count <= max_tries:
        images = soup.find_all('img', attrs={'class': 'image lazyloaded'})
    
        if len(images) == 1:
            img_text = extract_text(images[0])
            send_success_mail(img_text)
            # success
            success = True
            t_count = max_tries + 1
        else:
            t_count += 1

    if not success:
        # send error Email
        print("Error")


    # sender = "a.schaufelbuehl@hotmail.com"
    # recipient = "andreas.schaufelbuehl@gmail.com"
    # message = "Hello world!"

    # content = text.replace("\n", "")


    # email = EmailMessage()
    # email["From"] = sender
    # email["To"] = recipient
    # email["Subject"] = 'M-Outlet Notifier'
    # email.set_content(text)

    # smtp = smtplib.SMTP("smtp.office365.com", port=587)
    # smtp.starttls()
    # smtp.login(sender, "Vn3975nW8bPRfKW")
    # smtp.sendmail(sender, recipient, email.as_string())
    # smtp.quit()
    print("Done")

