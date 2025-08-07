import pathlib
import os 

pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

def folds(nammo,pathos="scraped"):
    print(f"{os.getcwd()}/{pathos}/{nammo}")
    try:
        os.mkdir(f"{os.getcwd()}/{pathos}/{nammo}")
        os.mkdir(f"{os.getcwd()}/{pathos}/{nammo}/dumps")
        print(f"Folder created successfully.")
    except FileExistsError:
        print(f"Folder already exist.")
    except PermissionError:
        print(f"Permission denied.")
    except Exception as e:
        print(f"An error occurred: {e}")


# folds("carlos_marin")

# folds("charlene_chua")

import datetime 
import pytz
import pandas as pd

import pathlib
import os 

pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

today = datetime.datetime.now()
scrape_time = today.astimezone(pytz.timezone("Australia/Brisbane"))
format_scrape_time = datetime.datetime.strftime(scrape_time, "%Y_%m_%d_%H")

dayo = datetime.datetime.today().weekday()
secondo = False
if dayo % 2 == 0:
    secondo = True

thirdo = False
if dayo % 3 == 0:
    thirdo = True

print(thirdo)

