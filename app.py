import schedule
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pytesseract
from PIL import Image
from bs4 import BeautifulSoup



def work():
    print("Study and work hard")



schedule.every(10).seconds.do(work)


if __name__ == "__main__":
    # Loop so that the scheduling task
    # keeps on running all time.
    while True:
 
        # Checks whether a scheduled task 
        # is pending to run or not
        schedule.run_pending()
        time.sleep(1)


        #conda install -c conda-forge opencv