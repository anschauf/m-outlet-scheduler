# M-Outlet Scheduler

Small python application, which runs periodically and checks [Zurich Migros Outlet](https://zuerich.migros.ch/de/outlet-migros.html) for discount promitions which are in my interest (e.g. Lego, Spielsachen,..).

The application runs as a cron-job using the instances provided by [Github Actions](https://github.com/features/actions). It scraped for the discount promotion image and extracts the text out of it. If any text of interest is found, it triggers an E-Mail notification.

Additionally, it stores all scraped image together with additional image data in Google Drive.

## Setup locally

- Make sure, chrome-driver is install on your Laptop:  `brew cask install chromedriver`
- Allow chrome-driver to access data -> see [Stackoverflow-Post](https://stackoverflow.com/a/60362134)
- create a new conda-environment: `conda create -n [ENV]` && `conda activate [ENV]`
- Install all libraries (requirements.txt): ` conda install [ALL_LIBS]`
- Alternatively install pip by `conda install pip`
- And install libraries via pip (copy the list of libraries): `pip install [...]`
- Duplicate `.env-example` to `.env` and fill all environment variables


## Internal Links

- [Google Colab: First POC of project](https://colab.research.google.com/drive/1V_yaRRbJr3bQtxlNhUXgt_SVIKMVAh7G?usp=sharing)
- [Github Repository (this one)](https://github.com/anschauf/m-outlet-scheduler)
- [Google Drive M-outlet Scheduler Storage](https://drive.google.com/drive/folders/1PwB_NHxu-gTf1cL9V73QJk1xMT3irMeZ?usp=drive_link)
- [Notion project documentation](https://www.notion.so/M-Outlet-Notifier-4136d64fabe942e2b09c1721acd59bcc?pvs=4)
- [Google Cloud: IAM Verwaltung M-Outlet Notifier](https://console.cloud.google.com/iam-admin/serviceaccounts/details/107968884044693374438;edit=true?project=m-outlet-notifier)


## Further reading and Sources used
- [Python: Read a Google Sheet file](https://www.youtube.com/watch?v=82DGz7IxW7c)
- [GSpread Usage Documentation](https://docs.gspread.org/en/latest/user-guide.html)
- [Youtube - Upload files to Google Drive (old)](https://www.youtube.com/watch?v=cCKPjW5JwKo)
- [Google Drive API - Upload Files](https://www.youtube.com/watch?v=cCKPjW5JwKo)
- [Stackoverflow: Upload image to Google Drive in Python](https://stackoverflow.com/questions/75987973/uploading-image-to-google-drive-in-python)
- [Zurich Migros Outlet](https://zuerich.migros.ch/de/outlet-migros.html)