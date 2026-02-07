# %%

import requests
import pandas as pd

import pathlib
import os 
from bs4 import BeautifulSoup as bs
from feedgen.feed import FeedGenerator

pathos = pathlib.Path(__file__).parent
os.chdir(pathos)
from dateutil import tz
import datetime 
import pytz

today = datetime.datetime.now()
scrape_time = today.astimezone(pytz.timezone("Australia/Brisbane"))
format_scrape_time = datetime.datetime.strftime(scrape_time, "%Y_%m_%d_%H")

# %%

urlo = "https://en.wikipedia.org/wiki/Special:Random"


def make_feed(frame, who,site, siteurl, out_path):

    entries = frame.copy()
    entries['Published'] = pd.to_datetime(entries['Published'], format="%Y_%m_%d_%H").dt.tz_localize(tz.tzlocal())

    fg = FeedGenerator()
    fg.id(f'{siteurl}')
    fg.title(f'{who} {site}')
    fg.author( {'name':f'{who}'} )
    fg.description("Hi")

    fg.link( href=f'{siteurl}', rel='self' )
    fg.language('en')

    for ind in entries.index:

        fe = fg.add_entry()
        fe.id(entries['Url'][ind])
        fe.title(entries['Headline'][ind])
        fe.link(href=entries['Url'][ind])
        fe.description(entries['Who'][ind])
        fe.published(entries['Published'][ind])

    # print(f'{out_path}/rss.xml')
    fg.rss_str(pretty=True)
    rssfeed  = fg.rss_str(pretty=True)
    fg.rss_file(f'scraped/{out_path}/rss.xml') 

# %%

records = []

for i in range(0, 5):
# for i in range(0, 1):

    # r = requests.get(urlo)

    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
    'Accept-Language': "en-GB,en-US;q=0.9,en;q=0.8",
    "Referer": 'https://www.google.com',
    "DNT":'1'}

    r = requests.get(urlo, headers=headers)

    soup = bs(r.content, 'html.parser')

    # print(r.text)
    # print(soup.title.string)
    record = {
        "Who":"Random wiki",
        "scraped_datetime":format_scrape_time,
        "Headline":soup.title.string.replace("- Wikipedia",'').strip(),
        "Url":r.url,
        "Site":"Wikipedia",
        "Siteurl":"https://en.wikipedia.org",
        "Published":format_scrape_time
    }

    records.append(record)

    # print(i)

frame = pd.DataFrame.from_records(records)

# print(frame)
# print(frame.columns.tolist())


make_feed(frame, "Wiki", 'en.wikipedia.org', 'https://en.wikipedia.org', 'wiki_random')

# def make_feed(frame, who,site, siteurl, out_path):