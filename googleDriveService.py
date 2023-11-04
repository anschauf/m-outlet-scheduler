import os
import re
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from datetime import date, datetime



class GoogleDriveService:
    def __init__(self):
        load_dotenv()

        self._SCOPES=['https://www.googleapis.com/auth/drive']

        gd_project_id = os.environ['GD_PROJECT_ID']
        pd_private_key_id = 'c006e3879b527533a734a794ddf1a140fa10b034'
        gd_private_key = os.environ['GD_PRIVATE_KEY']
        gd_client_email = os.environ['GD_CLIENT_EMAIL']
        gd_client_id = os.environ['GD_CLIENT_ID']

        print('GD_PROJECT_ID: ' + gd_project_id)
        print('GD_PRIVATE_KEY_ID: ' + pd_private_key_id)
        print('GD_PRIVATE_KEY: ' + gd_private_key)
        print('GD_CLIENT_EMAIL: ' + gd_client_email)
        print('GD_CLIENT_ID: ' + gd_client_id)
              
        # Credentials read from environment variables
        g_credentials = {
            "type": "service_account",
            "project_id": gd_project_id,
            "private_key_id": pd_private_key_id,
            "private_key": gd_private_key,
            "client_email": gd_client_email,
            "client_id": gd_client_id,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/m-outlet-executor%40m-outlet-notifier.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
        }

        # g_credentials = {
        #     "type": "service_account",
        #     "project_id": 'm-outlet-notifier',
        #     "private_key_id": 'c006e3879b527533a734a794ddf1a140fa10b034',
        #     "private_key": '-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCZ+8LYV5stQcbr\nWtpI00vf4nbXXkw9AuhMerHfZa2s8HKSJrw/AriU0KodLqGN8yn1TzyCr0tRttsx\n2lboJEJHeyjuO/vYbZwt1SuUfyDT/r7SWUjTPaGOzfN3Yhmn9qDrQMVM9HOf21Gl\nsSsugwI9KMwBg0yAh9JfVQ5nOj2OhD3EIbFHyf5Sz3NRdPhzCdGemnbxAw60zhdH\nLh1kVno1Vjj/71skE5aUyiAmRxXUH2avtqCOHqMrLJPF3TTXPvAS0Wcw3BLCSb+i\nbzTMFCr+PXghwMuo4d3bBhZBg8eiI67v6bIWWKA1ztdDrc5oTQU+00p8A7EpKwnT\ntU1pVKC1AgMBAAECggEAFt2v/Xhk7r+JzoFbUN0vsztp8mlqYNUBsfm2WDo9JCVA\nnjtqUOESj+a8nEDEdNPbMzZlAfMN+EBzJGAL78USopLDbT0zFNySCKxTIGYQdeqq\nY4omqlfImfAza1MCBFM3ajfgFKFoWiCzayt4AhwqRPK9+KuKvLtungF/dgzL/1Gg\n6p+goX9N6yRYnNVfh1Ab4VTIk5whGlgeUpbtSksDXGs25J0ArjKobihXr8CJEuJZ\nWMaeJ023HizZckYYPt9lLnfZvOiOsqlU0qHjeMSqI3pU+RO1QUB3BklLbOSPfjFY\nyLkZJn1XCr0XV57smfs9XQoubbpdO20hxYkMcrzTMQKBgQDNOcuP0iWCzeBy28x9\nWqBC8tamW4mz+y/jBeOmtjeN/p3f5hyWaN0vKRZplzAg7yFj5mqXO/WHCixwF682\nK5tZsjhuVewj/fJ0TCuR+NDdSaAYgNY2KapYhVMnXx/9C8cGTqRjeCqWXZOcXVOj\nReHxMvV8g51TjnsJTrN6gcmbwwKBgQDAFHnR4jssOW5t9mUhbhIkC5pO1mBLFmPK\nH0Wga50koGX6njFTvwSQ2xwK8Vv1ioSvr4TiIOvO5n/H86MJzF8xbCUDrEOytPpm\nEFOt6J5z5YeUx7l9e0dL6uRyWgZzf4HUCAVjrDa7PkqJleeUA82vw7KSu+ColDT3\n7TSytnoiJwKBgCESPDR79+GBTbcUpnpY3VSMj3yVabZgNxJNg6b83Cz8p/JJwbeX\nRHVyGJOBcpcMEgRoQCsI1YMiZ5DUsD55fnpQ1vkozXnrVWPaVncacoYGdE8ei+aE\nhlfnfEPu91euyy7AA4un9KzwfXYIMA8ylrtoq9iZ2QN7BWa1kQSf355DAoGAQbo/\n/Vwm13lHmoVIEepydrcptHSTOt6Mgyu0TbLFcTUZ8GqVgozI6TCxJeV1jE48HUo4\ndJDDYGdrrmZmkgHHSUgyWlFmUQ6w6KAJomcJYatXe8fkZ1X6DbZxOdgogPlO2dls\nzrCtgeFM7EvJlNLAXbbfsmpr9APTJEudTtI2dN0CgYBNLDgYlbCSfsBpJl9isMQN\nMEU46AG0w7BAtEX57AgNX5NTyKbmAjIvvBWLTL7kK9aQGMihGuinqABFBEHHBHq/\nDGXxkIEpEliA8vV0hRMuJmjh7Vv399wflQ//CoehpK45QRlluuzXB9L8/quHgJjR\nZlrkz2XuX5Jc/CvZZMrhhQ==\n-----END PRIVATE KEY-----\n',
        #     "client_email": 'm-outlet-executor@m-outlet-notifier.iam.gserviceaccount.com',
        #     "client_id": '107968884044693374438',
        #     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        #     "token_uri": "https://oauth2.googleapis.com/token",
        #     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        #     "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/m-outlet-executor%40m-outlet-notifier.iam.gserviceaccount.com",
        #     "universe_domain": "googleapis.com"
        # }

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

        