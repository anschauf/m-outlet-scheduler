import os
import re
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from datetime import date, datetime



class GoogleDriveService:
    def __init__(self):
        self._SCOPES=['https://www.googleapis.com/auth/drive']


        print('GD_PROJECT_ID: ' + os.environ['GD_PROJECT_ID'])
        print('GD_PRIVATE_KEY_ID: ' + os.environ['GD_PRIVATE_KEY_ID'])
        print('GD_PRIVATE_KEY: ' + os.environ['GD_PRIVATE_KEY'])
        print('GD_CLIENT_EMAIL: ' + os.environ['GD_CLIENT_EMAIL'])
        print('GD_CLIENT_ID: ' + os.environ['GD_CLIENT_ID'])
              
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
        self.service = build('drive', 'v3', credentials=creds)

        self.g_spread_file_name = 'm_outlet_actions'
        self.gdrive_img_folder = os.environ['GD_IMAGE_FOLDER_ID']

        
        # service = build('drive', 'v3', credentials=creds)
        # self.service = service

    
    def get_latest_image_url(self, filename):
        try:
            mysheet = self.client.open(self.g_spread_file_name).sheet1

            rows = mysheet.get_all_records()

            return rows[-1]['image_url']
        except Exception as e:
            print(f'Error accessing Google Spread file {filename}')


    def append_new_image_data(self, image_url_small, img_text, matching_regex, img_filename):
        today_date = str(date.today())

        if len(matching_regex) > 0:
            has_matches = True
        else:
            has_matches = False


        mysheet = self.client.open(self.g_spread_file_name).sheet1
        rows = mysheet.get_all_records()
        latest_end_date = rows[-1]['end_date']
        old_id = rows[-1]['id']
        curr_id = old_id + 1

        clean_img_text = img_text.replace(',', ';').replace('\n', '  ')
        body = [str(curr_id), today_date, '', image_url_small, str(has_matches), str(matching_regex), img_filename, clean_img_text]



        # Update the end date of the old action, if empty.
        if len(latest_end_date) <= 0:
            mysheet.update_cell(row=len(rows), col=2, value=today_date)

        # Append new action.
        mysheet.append_row(body)
        # mysheet.append_row(body, table_range="A1:F1")
        print('Wrote new image data to GSpread file.')

        return curr_id
    
    def upload_image(self, local_img_path, img, image_url_small):
        try:
            # Save image
            img.save(local_img_path)

            # add leading zeros
            # id_str = str(id).zfill(3)
            curr_date = datetime.now()
            now_year = curr_date.strftime("%Y")
            kw = re.search('(KW\d\d).\w{3}', image_url_small).group(0)

            file_name = f'm_outlet_{now_year}_{kw}'
            file_metadata = {'name': file_name, 'parents': [self.gdrive_img_folder]}

            mime_type = f'image/{kw[-3:]}'
            media = MediaFileUpload(local_img_path, mimetype=mime_type)

            # Upload to Google Drive
            file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print(f"Image with ID '{file.get('id')}' was uploaded to the folder with ID  on Google Drive")
            return file_name
        except Exception as e:
            return f'Upload image to Google drive failed with: {e}'

        