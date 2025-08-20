
# %%

import random
import pandas as pd 
import requests
import json
import re

import matplotlib.pylab as pylt
pylt.rcParams['figure.dpi'] = 200
import seaborn as sns
import matplotlib.pyplot as plt 
%matplotlib inline

from feedgen.feed import FeedGenerator
from sudulunu.helpers import pp, dumper
from dateutil import tz
import pathlib
import os 
import datetime 
import pytz

pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

today = datetime.datetime.now()
scrape_time = today.astimezone(pytz.timezone("Australia/Brisbane"))
format_scrape_time = datetime.datetime.strftime(scrape_time, "%Y_%m_%d_%H")

# %%



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

INVALID_XML_RE = re.compile(
    r"[^\x09\x0A\x0D\x20-\uD7FF\uE000-\uFFFD\U00010000-\U0010FFFF]"
)

def clean_xml_text(text):
    if isinstance(text, str):
        return INVALID_XML_RE.sub("", text)
    return text


def json_grabber(pathos, out_path):

    r = requests.get(pathos)
    jsony = json.loads(r.text)

    datah = pd.DataFrame(jsony['articles'])

    # ['publication', 'twitterHandle', 'blueSkyHandle', 'url', 'headline', 'image', 'timestamp', 'isTemplated', 'mastodonHandle']

    datah = datah.loc[datah['timestamp'] != 'none']
    datah['timestamp'] = pd.to_datetime(datah['timestamp'], errors='coerce')
    datah.dropna(subset=['timestamp'], inplace=True)
    datah['timestamp'] = datah['timestamp'].dt.strftime("%Y_%m_%d_%H")

    datah.sort_values(by=['timestamp'], ascending=False, inplace=True)

    datah.dropna(subset=['headline', 'timestamp', 'publication', 'url'], inplace=True)

    datah.rename(columns={'publication': "Who", 'timestamp': "Published", 'headline': "Headline", 'url': "Url"}, inplace=True)
    datah = datah[['Who', 'Url', 'Headline', 'Published']]

    for col in datah.columns.tolist():
        datah[col] = datah[col].apply(clean_xml_text)

    dumper(f'scraped/{out_path}', f"latest", datah)
    dumper(f'scraped/{out_path}/dumps', f"{format_scrape_time }", datah)

    datah = datah[:20]

    # pp(datah)

    make_feed(datah, "Interactives","Interactives", "https://github.com/sammorrisdesign/interactive-feed", out_path)


json_grabber('https://raw.githubusercontent.com/sammorrisdesign/interactive-feed/refs/heads/main/data/all.json', 'bsky_interactives')

# %%

