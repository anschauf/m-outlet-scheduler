import os
import io
import re
import requests
import pytesseract

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from services.emailService import send_success_mail, send_failed_mail
from services.googleDriveService import GoogleDriveService


# https://stackoverflow.com/a/61157968
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)

# Basic config
app_name = 'M-Outlet Notifier'
img_file_path = 'image.png'
base_url = "https://zuerich.migros.ch/de/outlet-migros.html"
image_base_url = 'https://zuerich.migros.ch'
gspread_image_date_file_id = '1FNzPArr137RIT_kW_70m2l68S7kxKC8kp51tCeM8mOU'

driver.get(base_url)
content = driver.page_source
soup = BeautifulSoup(content)


# REGED Rules it needs to match
regex_rules = [
    'spiel',
    'lego',
    'klemmbau',
    'steine',
    'non.?food' # non-food in any variation in-between space, e.g. non-food, nonfood, non food
]



def extract_text(html_image):
    '''
    Extract text from the scraped image. 
    It gets the big image first for better resolution.
    '''

    image_url_small = image_base_url + html_image['src']
    # replace 'small' with 'large' in URL -> get the big image.
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


def find_regex_rules(extracted_text: str):
    '''
    Search for any appearances of the global regex rules
    within the provided text.
    '''
    matches = []

    for rr in regex_rules:
        match = re.search(rr, extracted_text, re.IGNORECASE)
        if match:
            matches.append(rr)
    
    return matches

def clean_up():
    '''
    General clean up task at the end of the app.
    '''
    if os.path.exists(img_file_path):
        os.remove(img_file_path)
    


if __name__ == "__main__":
    load_dotenv()

    googleDriveService = GoogleDriveService()
    gd_latest_image_url = googleDriveService.get_latest_image_url(gspread_image_date_file_id)


    # Sometimes browser was not ready -> img source is not found.
    # Multiple tries heuristicly leads to a mostly succesful run.
    max_tries = 5
    t_count = 0

    image_scrape_success = False

    while t_count < max_tries:
        html_images = soup.find_all('img', attrs={'src': re.compile(r'(KW\d\d)')})
        # html_images = soup.find_all('img', attrs={'class': 'image lazyloaded'})

        if len(html_images) == 1:
            # Image found
            image_scrape_success = True
            html_image = html_images[0]
            image_url_small = image_base_url + html_image['src']

            if gd_latest_image_url != image_url_small:
                # New Image found
                print(f'Found new image on the website with URL: {image_url_small}')

                try:
                    img_text, image_big, image_small = extract_text(html_image)
                    matching_regex = find_regex_rules(img_text)

                    if len(matching_regex) > 0:
                        # Matching rule found
                        send_success_mail(app_name, img_file_path, base_url, img_text, image_small, matching_regex)
                    
                    img_filename = googleDriveService.upload_image(local_img_path=img_file_path, img=image_big, image_url_small=image_url_small)
                    googleDriveService.append_new_image_data(image_url_small, img_text, matching_regex, img_filename)
                    t_count = max_tries
                except Exception as e:
                    send_failed_mail(str(e), 'Exception')
                    t_count = max_tries
            else:
                print("The image found is already logged.")
                t_count = max_tries
        else:
            t_count += 1
            print(f'Image scrape try #{t_count}. Found {len(html_images)} images')
    
    if not image_scrape_success and t_count >= max_tries:
        print(f'Looped more than {max_tries}')
        send_failed_mail(f'Looped more than {max_tries}', 'Loop end', app_name)

    clean_up()
    print("M-Scheduler has run through.")

