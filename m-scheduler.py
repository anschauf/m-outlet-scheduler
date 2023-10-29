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


driver.get("https://zuerich.migros.ch/de/outlet-migros.html")
content = driver.page_source
soup = BeautifulSoup(content)

# Mail configs
sender = os.environ['SENDER']
recipient = os.environ['RECEIPIENT']
password = os.environ['PASSWORD']

app_name = 'M-Outlet Notifier'
img_file_path = 'image.png'


def extract_text(html_image):
    base_url = 'https://zuerich.migros.ch'
    image_url_small = base_url + html_image['src']
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

def send_success_mail(img_text: str, img_before):
    # save image
    img_before.save(img_file_path)


    msg = MIMEMultipart('alternative')

    msg['Subject'] = "M-Outlet Notifier"
    msg['From'] = sender
    msg['To'] = recipient

    text = MIMEText('<img src="cid:image1">', 'html')
    msg.attach(text)

    image = MIMEImage(open(img_file_path, 'rb').read())

    # Define the image's ID as referenced in the HTML body above
    image.add_header('Content-ID', '<image1>')
    msg.attach(image)


    # email = EmailMessage()
    # email["From"] = app_name
    # email["To"] = recipient
    # email["Subject"] = f'{app_name}: Interessante Aktion'
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

def clean_up():
    os.remove(img_file_path)
    


if __name__ == "__main__":
    load_dotenv()
    # images = soup.find_all(attrs={'class': 'image lazyloaded'})
    max_tries = 5
    t_count = 0
    success = False

    try:
        while success == False and t_count <= max_tries:
            html_images = soup.find_all('img', attrs={'class': 'image lazyloaded'})
        
            if len(html_images) == 1:
                img_text, image_big, image_small = extract_text(html_images[0])
                send_success_mail(img_text, image_small)
                # success
                success = True
                t_count = max_tries + 1
            else:
                t_count += 1
    except Exception as e:
        send_failed_mail(str(e), 'Exception')


    if not success:
        # send error Email
        send_failed_mail(f'Looped more than {max_tries}', 'Loop end')


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
    clean_up()
    print("Done")

