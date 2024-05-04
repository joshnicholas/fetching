from feedgen.feed import FeedGenerator
import pandas as pd
import dateparser
import datetime 
from dateutil import tz

import pathlib
import os 
pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

print(os.getcwd())

def make_feed(frame, who,site, siteurl, out_path):

    entries = frame.copy()
    entries['Published'] = pd.to_datetime(entries['Published'], format="%Y_%m_%d_%H").dt.tz_localize(tz.tzlocal())

    fg = FeedGenerator()
    fg.id(f'{siteurl}')
    fg.title(f'{site}')
    fg.author( {'name':f'{who}'} )
    fg.description("Hi")

    fg.link( href=f'{siteurl}', rel='self' )
    fg.language('en')

    for ind in entries.index:

        fe = fg.add_entry()
        fe.id(entries['Url'][ind])
        fe.title(entries['Headline'][ind])
        fe.link(href=entries['Siteurl'][ind])
        fe.description(entries['Who'][ind])
        fe.published(entries['Published'][ind])

    print(f'{out_path}/rss.xml')
    fg.rss_str(pretty=True)
    rssfeed  = fg.rss_str(pretty=True)
    fg.rss_file(f'scraped/{out_path}/rss.xml') 


data = pd.read_csv('scraped/sean_kelly/latest.csv')

make_feed(data, 'Sean Kelly', 
'SMH','https://www.smh.com.au/', "sean_kelly")




