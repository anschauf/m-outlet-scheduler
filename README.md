# M-Outlet Scheduler


## Setup locally

- Make sure, chrome-driver is install on your Laptop:  `brew cask install chromedriver`
- Allow chrome-driver to access data -> see [Stackoverflow-Post](https://stackoverflow.com/a/60362134)
- create a new conda-environment: `conda create -n [ENV]` && `conda activate [ENV]`
- Install all libraries (requirements.txt): ` conda install [ALL_LIBS]`
- Alternatively install pip by `conda install pip`
- And install libraries via pip (copy the list of libraries): `pip install [...]`
- Duplicate `.env-example` to `.env` and fill all environment variables

## Links
- [Python: Read a Google Sheet file](https://www.youtube.com/watch?v=82DGz7IxW7c)
- [GSpread Usage Documentation](https://docs.gspread.org/en/latest/user-guide.html)