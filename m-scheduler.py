import os
import io
import re
import requests
import pytesseract
import smtplib


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from bs4 import BeautifulSoup
from email.message import EmailMessage
from dotenv import load_dotenv

from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


# https://stackoverflow.com/a/61157968
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)

app_name = 'M-Outlet Notifier'
img_file_path = 'image.png'
base_url = "https://zuerich.migros.ch/de/outlet-migros.html"

driver.get(base_url)
content = driver.page_source
soup = BeautifulSoup(content)

# Mail configs
sender = os.environ['SENDER']
recipient = os.environ['RECEIPIENT']
password = os.environ['PASSWORD']


# regex rules
reges_rules = [
    'spiel',
    'lego',

    ## testing
    'glih',
    'ochen',
]



def extract_text(html_image):
    image_base_url = 'https://zuerich.migros.ch'
    image_url_small = image_base_url + html_image['src']
    # replace 'small' with 'large' in URL
    image_url_big = image_url_small.replace('small', 'large', 1)

    image_content_big = requests.get(image_url_big).content
    image_file_big = io.BytesIO(image_content_big)

    image_content_small = requests.get(image_url_small).content
    image_file_small = io.BytesIO(image_content_small)

    # Extract the text from the image
    image_big = Image.open(image_file_big)
    image_small = Image.open(image_file_small)

    # Perform OCR using PyTesseract
    text = pytesseract.image_to_string(image_big)
    return text, image_big, image_small 

def send_success_mail(img_text: str, img_before, matching_regex):
    # save image
    img_before.save(img_file_path)


    msg = MIMEMultipart('alternative')

    msg['Subject'] = f"{app_name}: Interessante Aktion"
    msg['From'] = sender
    msg['To'] = recipient

    regex_rules_msg = ''
    for mr in matching_regex:
        regex_rules_msg += f'<li>{mr}</li>'

    text = MIMEText(f"""
                    <div>
                        <h1> Interessante Aktion: </h1>
                        <a href="{base_url}">
                        <img src="cid:image1">
                        </a>
                    </div>
                    <br>
                    <br>
                    <div>
                        <h4> Folgende Regel(n) haben angeschlagen: </h4>
                            <ul>
                                {regex_rules_msg}
                            </ul>
                    </div>
                    <br>
                    <div>
                        <h4> Extrahierter Text: </h4>
                        <div style="background-color:#6C6C6C ; padding:10px; border-radius: 15px">
                            {img_text}
                        </div>
                    </div>
                    """, 'html')
    msg.attach(text)

    image = MIMEImage(open(img_file_path, 'rb').read())

    # Define the image's ID as referenced in the HTML body above
    image.add_header('Content-ID', '<image1>')
    msg.attach(image)


    # email = EmailMessage()
    # email["From"] = app_name
    # email["To"] = recipient
    # email.set_content(img_text)

    smtp = smtplib.SMTP("smtp.office365.com", port=587)
    smtp.starttls()
    smtp.login(sender, password)
    smtp.sendmail(sender, recipient, msg.as_string())
    smtp.quit()

def send_failed_mail(e, subject: str):
    email = EmailMessage()
    email["From"] = app_name
    email["To"] = recipient
    email["Subject"] = f'{app_name}: Exception occured - {subject}'
    email.set_content(e)

    smtp = smtplib.SMTP("smtp.office365.com", port=587)
    smtp.starttls()
    smtp.login(sender, password)
    smtp.sendmail(sender, recipient, email.as_string())
    smtp.quit()


def find_regex_rules(extracted_text):
    matches = []

    for rr in reges_rules:
        match = re.search(rr, extracted_text, re.IGNORECASE)
        if match:
            matches.append(rr)
    
    return matches

def clean_up():
    if os.path.exists(img_file_path):
        os.remove(img_file_path)
    


if __name__ == "__main__":
    load_dotenv()
    max_tries = 5
    t_count = 0

    image_scrape_success = False

    while t_count < max_tries:
        html_images = soup.find_all('img', attrs={'class': 'image lazyloaded'})

        if len(html_images) == 1:
            # Image found
            image_scrape_success = True
            try:
                img_text, image_big, image_small = extract_text(html_images[0])
                matching_regex = find_regex_rules(img_text)

                if len(matching_regex) > 0:
                    # Matching rule found
                    send_success_mail(img_text, image_small, matching_regex)
                    
  
                t_count = max_tries
            except Exception as e:
                send_failed_mail(str(e), 'Exception')
                t_count = max_tries
        else:
            t_count += 1
    
    if not image_scrape_success and t_count >= max_tries:
        send_failed_mail(f'Looped more than {max_tries}', 'Loop end')

    clean_up()
    print("Done")

