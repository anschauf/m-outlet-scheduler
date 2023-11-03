import os
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from datetime import date

g_spread_file_name = 'm_outlet_actions'

class GoogleDriveService:
    def __init__(self):
        self._SCOPES=['https://www.googleapis.com/auth/drive']

                # Credentials read from environment variables
        g_credentials = {
            "type": "service_account",
            "project_id": os.environ['GD_PROJECT_ID'],
            "private_key_id": os.environ['GD_PRIVATE_KEY_ID'],
            "private_key": os.environ['GD_PRIVATE_KEY'],
            "client_email": os.environ['GD_CLIENT_EMAIL'],
            "client_id": os.environ['GD_CLIENT_ID'],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/m-outlet-executor%40m-outlet-notifier.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
        }

        creds = ServiceAccountCredentials._from_parsed_json_keyfile(g_credentials, self._SCOPES)
        self.client = gspread.authorize(creds)

        
        # service = build('drive', 'v3', credentials=creds)
        # self.service = service

    
    def get_latest_image_url(self, filename):
        try:
            mysheet = self.client.open(g_spread_file_name).sheet1

            rows = mysheet.get_all_records()

            return rows[-1]['image_url']
        except Exception as e:
            print(f'Error accessing Google Spread file {filename}')


    def append_new_image_data(self, image_url_small, img_text, matching_regex):
        today_date = str(date.today())

        if len(matching_regex) > 0:
            has_matches = True
        else:
            has_matches = False

        clean_img_text = img_text.replace(',', ';')
        body = [today_date, '', image_url_small, clean_img_text, str(has_matches), str(matching_regex)]

        mysheet = self.client.open(g_spread_file_name).sheet1
        
        rows = mysheet.get_all_records()
        latest_end_date = rows[-1]['end_date']

        # Update the end date of the old action, if empty.
        if len(latest_end_date) <= 0:
            mysheet.update_cell(row=len(rows), col=2, value=today_date)

        # Append new action.
        mysheet.append_row(body)
        # mysheet.append_row(body, table_range="A1:F1")
        print('Wrote new image data to GSpread file.')