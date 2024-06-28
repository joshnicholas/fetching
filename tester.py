from playwright.sync_api import sync_playwright
# from playwright_stealth import stealth_sync
from feedgen.feed import FeedGenerator

from dateutil import tz
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

def make_path(out_path):
    already_there = os.listdir("scraped")

    if out_path not in already_there:
        # print('SOMETHING')
        os.mkdir(f"scraped/{out_path}")
        os.mkdir(f"scraped/{out_path}/dumps")

def dumper(path, name, frame):
    with open(f'{path}/{name}.csv', 'w') as f:
        frame.to_csv(f, index=False, header=True)

def rand_delay(num):
  import random 
  import time 
  rando = random.random() * num
#   print(rando)
  time.sleep(rando)

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

def shot_grabber(tries, urlo, who,site, siteurl, out_path,  javascript_code, awaito, wait=False):
    print(f"\nScraping {who}")
    make_path(out_path)
    # tries = 0
    try:
        with sync_playwright() as p:
            browser = p.firefox.launch()
            # browser = p.chromium.launch()

            context = browser.new_context()

            page = context.new_page()


            page.goto(urlo)

            if wait:
                print('Waiting')
                waiting_around = page.locator(awaito)
                waiting_around.wait_for()
                print("Waited")

            resulto = page.evaluate(javascript_code)

            # print("Resulto: ", resulto)

            context.close()
            browser.close()

            frame = pd.DataFrame.from_records(resulto)

            frame = frame[:10]

            frame['Who'] = who

            frame['Site'] = site

            frame['Siteurl'] = siteurl

            frame['scraped_datetime']= format_scrape_time 

            frame = frame[['Who', 'scraped_datetime', 'Headline', 'Url', 'Site', 'Siteurl', 'Published']]

            frame['Published']= pd.to_datetime(frame['Published'], utc=True)
            frame.sort_values(by=['Published'], ascending=False, inplace=True)
            frame['Published'] = frame['Published'].dt.strftime("%Y_%m_%d_%H")

            dumper(f'scraped/{out_path}', f"latest", frame)
            dumper(f'scraped/{out_path}/dumps', f"{format_scrape_time }", frame)

            rand_delay(5)

            make_feed(frame,who,site, siteurl, out_path)
            # return frame 

    except Exception as e:
        tries += 1
        print("Tries: ", tries)
        # context.close()
        # browser.close()
        print(e)
        rand_delay(5)
        if tries <= 3:
        # if e == 'Timeout 30000ms exceeded.' and tries <= 3:
            print("Trying again")
            shot_grabber(tries, urlo, who,site, siteurl, out_path,  javascript_code, awaito, wait)



# shot_grabber(0,'https://www.theage.com.au/by/daniel-brettig-p4ywcj','Daniel Brettig', 
# 'The Age','https://www.theage.com.au/', "daniel_brettig",
# """
# Array.from(document.querySelectorAll('._3SZUs,.X3yYQ'), el => {
# let Headline = el.querySelector('h3').innerText;
# let Url = el.querySelector('a')['href']
# let Published = el.querySelector('._2_zR-')['dateTime']
# return {Headline, Url, Published};
# })""",
# '._2VCps _2GpEY')





