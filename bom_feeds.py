# %%

import feedparser
import sys
from datetime import datetime
import requests
import pandas as pd 
import re
import dateparser 
import random 
import time 
import pytz
from dateutil import tz
from feedgen.feed import FeedGenerator
melbourne_tz = pytz.timezone('Australia/Melbourne')

def rand_delay(num):
  rando = random.random() * num
#   print(rando)
  time.sleep(rando)

def read_rss_feed(url):
    try:

        feed = feedparser.parse(url)
        

        print(f"Feed Title: {feed.feed.title}")
        print(f"Feed Description: {feed.feed.description}")
        print(f"Feed Link: {feed.feed.link}")
        print(f"Last Updated: {feed.feed.updated}")
        print("-" * 50)
        

        for i, entry in enumerate(feed.entries[:10], 1):

            print(f"\nEntry {i}:")
            print(f"Title: {entry.title}")
            print(f"Link: {entry.link}")
            print(f"Published: {entry.published}")
            print(f"Summary: {entry.summary[:200]}...")
            
    except Exception as e:
        print(f"Error reading feed: {e}")

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
'Accept-Language': "en-GB,en-US;q=0.9,en;q=0.8",
"Referer": 'https://www.google.com',
"DNT":'1'}

# %%

# read_rss_feed('https://www.bom.gov.au/fwo/IDZ00061.warnings_land_nsw.xml')

urlo = 'https://www.bom.gov.au/fwo/IDZ00054.warnings_nsw.xml'

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

urlos = [("NSW", 'https://www.bom.gov.au/fwo/IDZ00054.warnings_nsw.xml'),
("VIC", 'https://www.bom.gov.au/fwo/IDZ00059.warnings_vic.xml'),
("QLD", 'https://www.bom.gov.au/fwo/IDZ00056.warnings_qld.xml'),
("WA", 'https://www.bom.gov.au/fwo/IDZ00060.warnings_wa.xml'),
("SA", 'https://www.bom.gov.au/fwo/IDZ00057.warnings_sa.xml'),
("TAS", "https://www.bom.gov.au/fwo/IDZ00058.warnings_tas.xml"),
("NT", 'https://www.bom.gov.au/fwo/IDZ00055.warnings_nt.xml')
]

exclude = ['Thunderstorm', 'Surf Warning', 'Sheep Graziers', 'Marine Wind', 'Severe Weather Warning', 'Coastal Hazard Warning']

records = []

for thing in urlos:
    urlo = thing[1]
    statto = thing[0]

    feed = feedparser.parse(urlo,  request_headers=headers)

    for entry in feed['entries']:


        title = re.sub(r'\s+', ' ', entry['title']).strip()
        title = re.split(r'EDT|EST|CST|WST', title)[-1].strip()

        title = f"{statto}: {title}"

        parsed_date = dateparser.parse(entry['published'], date_formats=["%a, %d %b %Y %H:%M:%S %Z"])
        melbourne_tz = pytz.timezone('Australia/Melbourne')

        if parsed_date.tzinfo is None:
            utc_tz = pytz.UTC
            parsed_date = utc_tz.localize(parsed_date)
            
        melbourne_date = parsed_date.astimezone(melbourne_tz)

        datto = melbourne_date.strftime("%Y_%m_%d_%H")

        # datto = dateparser.parse(entry['published'], date_formats=["%a, %d %b %Y %H:%M:%S %Z"]).strftime("%Y_%m_%d_%H")

        if not any(s.lower() in title.lower() for s in exclude):

            # print(title)
            # print(datto)
            record = { "Published": datto, "Headline": title, "Url": urlo,"Who": "BOM" }
            records.append(record)
    rand_delay(2)
# %%
frame = pd.DataFrame(records)
# print(frame)
# print(records)

make_feed(frame, "BOM", 'Bom.gov.au', 'https://www.bom.gov.au/', 'bom_warnings')


# %%