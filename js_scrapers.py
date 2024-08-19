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

dayo = datetime.datetime.today().weekday()
secondo = False
if dayo % 2 == 0:
    secondo = True

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



shot_grabber(0,'https://www.theage.com.au/by/daniel-brettig-p4ywcj','Daniel Brettig', 
'The Age','https://www.theage.com.au/', "daniel_brettig",
"""
Array.from(document.querySelectorAll('._3SZUs,.X3yYQ'), el => {
let Headline = el.querySelector('h3').innerText;
let Url = el.querySelector('a')['href']
let Published = el.querySelector('._2_zR-')['dateTime']
return {Headline, Url, Published};
})""",
'._2VCps _2GpEY')

rand_delay(2)

if secondo:
    shot_grabber(0,'https://www.smh.com.au/by/sean-kelly-h1d26a','Sean Kelly', 
    'SMH','https://www.smh.com.au/', "sean_kelly",
    """
    Array.from(document.querySelectorAll('._3SZUs,.X3yYQ'), el => {
    let Headline = el.querySelector('h3').innerText;
    let Url = el.querySelector('a')['href']
    let Published = el.querySelector('._2_zR-')['dateTime']
    return {Headline, Url, Published};
    })""",
    '._2VCps _2GpEY')

    rand_delay(2)

if secondo:
    shot_grabber(0,'https://www.smh.com.au/by/the-visual-stories-team-p53776','SMH Visual Stories', 
    'SMH','https://www.smh.com.au/', "smh_visual_stories",
    """
    Array.from(document.querySelectorAll('._3SZUs,.X3yYQ'), el => {
    let Headline = el.querySelector('h3').innerText;
    let Url = el.querySelector('a')['href']
    let Published = el.querySelector('._2_zR-')['dateTime']
    return {Headline, Url, Published};
    })""",
    '._2VCps _2GpEY')

    rand_delay(2)

if not secondo:
    shot_grabber(0,'https://www.smh.com.au/by/craig-butt-hvf8q','Craig Butt', 
    'SMH','https://www.smh.com.au/', "craig_butt",
    """
    Array.from(document.querySelectorAll('._3SZUs,.X3yYQ'), el => {
    let Headline = el.querySelector('h3').innerText;
    let Url = el.querySelector('a')['href']
    let Published = el.querySelector('._2_zR-')['dateTime']
    return {Headline, Url, Published};
    })""",
    '._2VCps _2GpEY')

    rand_delay(2)


shot_grabber(0,'https://www.reuters.com/graphics/','Reuters Graphics', 
'Reuters','https://www.reuters.com', "reuters_graphics",
"""
Array.from(document.querySelectorAll('article.svelte-11dknnx,div.hero-row'), el => {

let Headline = el.querySelector('h2,h3').innerText;
let Url = el.querySelector('a')['href']
let Published = el.querySelector('small').innerText;
return {Headline, Url, Published};
})""",
'.hero-row clearfix')

rand_delay(2)

if secondo:
    shot_grabber(0,'https://www.scmp.com/infographic/#recentproj','SCMP Graphics', 
    'SCMP','https://www.scmp.com', "scmp_graphics",
    """
    Array.from(document.querySelectorAll('.half'), el => {
    let Headline = el.querySelector('h2').innerText;
    let Url = el.querySelector('a')['href']
    let Published = el.querySelector('.feed-date').innerText.split("|")
    Published = Published.pop().trim()

    return {Headline, Url, Published};
    })""",
    '.featureContainer')
        
    rand_delay(2)

shot_grabber(0,'https://www.abc.net.au/news/interactives','ABC Storylab', 
'ABC','https://www.abc.net.au', "abc_storylab",
"""
Array.from(document.querySelectorAll('[data-component="DetailCard"]'), el => {
let Headline = el.querySelector('h3').innerText;

let Url = el.querySelector('[data-component="Link"]')['href']
let Published = el.querySelector('time').getAttribute("datetime")

return {Headline, Url, Published};
})""",
'[data-component="Section"]')

rand_delay(2)

shot_grabber(0,'https://www.abc.net.au/news/alex-lim/103417492','ABC Alex Lim', 
'ABC','https://www.abc.net.au', "alex_lim",
"""
Array.from(document.querySelectorAll('[data-component="DetailCard"]'), el => {
let Headline = el.querySelector('h3').innerText;

let Url = el.querySelector('[data-component="Link"]')['href']
let Published = el.querySelector('time').getAttribute("datetime")

return {Headline, Url, Published};
})""",
'[data-component="Section"]')

rand_delay(2)

if secondo:
    shot_grabber(0,'https://www.abc.net.au/news/inga-ting/8749946','ABC Inga Ting', 
    'ABC','https://www.abc.net.au', "inga_ting",
    """
    Array.from(document.querySelectorAll('[data-component="DetailCard"]'), el => {
    let Headline = el.querySelector('h3').innerText;

    let Url = el.querySelector('[data-component="Link"]')['href']
    let Published = el.querySelector('time').getAttribute("datetime")

    return {Headline, Url, Published};
    })""",
    '[data-component="Section"]')

    rand_delay(2)

if not secondo:
    shot_grabber(0,'https://www.abc.net.au/news/madi-chwasta/13512978','Madi Chwasta', 
    'ABC','https://www.abc.net.au', "madi_chwasta",
    """
    Array.from(document.querySelectorAll('[data-component="DetailCard"]'), el => {
    let Headline = el.querySelector('h3').innerText;

    let Url = el.querySelector('[data-component="Link"]')['href']
    let Published = el.querySelector('time').getAttribute("datetime")

    return {Headline, Url, Published};
    })""",
    '[data-component="Section"]')

    rand_delay(2)

if secondo:
    shot_grabber(0,'https://www.abc.net.au/news/matt-liddy/201998','ABC Matt Liddy', 
    'ABC','https://www.abc.net.au', "matt-liddy",
    """
    Array.from(document.querySelectorAll('[data-component="DetailCard"]'), el => {
    let Headline = el.querySelector('h3').innerText;

    let Url = el.querySelector('[data-component="Link"]')['href']
    let Published = el.querySelector('time').getAttribute("datetime")

    return {Headline, Url, Published};
    })""",
    '[data-component="Section"]')

    rand_delay(2)

if secondo:
    shot_grabber(0,'https://www.abc.net.au/news/ben-spraggon/5449826','ABC Ben Spraggon', 
    'ABC','https://www.abc.net.au', "ben_spraggon",
    """
    Array.from(document.querySelectorAll('[data-component="DetailCard"]'), el => {
    let Headline = el.querySelector('h3').innerText;

    let Url = el.querySelector('[data-component="Link"]')['href']
    let Published = el.querySelector('time').getAttribute("datetime")

    return {Headline, Url, Published};
    })""",
    '[data-component="Section"]')

    rand_delay(2)

if secondo:
    shot_grabber(0,'https://www.abc.net.au/news/brody-smith/104177592','Brody Smith', 
    'ABC','https://www.abc.net.au', "brody_smith",
    """
    Array.from(document.querySelectorAll('[data-component="DetailCard"]'), el => {
    let Headline = el.querySelector('h3').innerText;

    let Url = el.querySelector('[data-component="Link"]')['href']
    let Published = el.querySelector('time').getAttribute("datetime")

    return {Headline, Url, Published};
    })""",
    '[data-component="Section"]')

    rand_delay(2)

if secondo:
    shot_grabber(0,'https://www.abc.net.au/news/mark-doman/2818976','ABC Mark Doman', 
    'ABC','https://www.abc.net.au', "mark_doman",
    """
    Array.from(document.querySelectorAll('[data-component="DetailCard"]'), el => {
    let Headline = el.querySelector('h3').innerText;

    let Url = el.querySelector('[data-component="Link"]')['href']
    let Published = el.querySelector('time').getAttribute("datetime")

    return {Headline, Url, Published};
    })""",
    '[data-component="Section"]')

    rand_delay(2)

if not secondo:
    shot_grabber(0,'https://www.abc.net.au/news/thomas-brettell/13785610','ABC Thomas Brettell', 
    'ABC','https://www.abc.net.au', "thomas_brettell",
    """
    Array.from(document.querySelectorAll('[data-component="DetailCard"]'), el => {
    let Headline = el.querySelector('h3').innerText;

    let Url = el.querySelector('[data-component="Link"]')['href']
    let Published = el.querySelector('time').getAttribute("datetime")

    return {Headline, Url, Published};
    })""",
    '[data-component="Section"]')

    rand_delay(2)

if not secondo:
    shot_grabber(0,'https://www.abc.net.au/news/katia-shatoba/12532552','ABC Katia Shatoba', 
    'ABC','https://www.abc.net.au', "katia_shatoba",
    """
    Array.from(document.querySelectorAll('[data-component="DetailCard"]'), el => {
    let Headline = el.querySelector('h3').innerText;

    let Url = el.querySelector('[data-component="Link"]')['href']
    let Published = el.querySelector('time').getAttribute("datetime")

    return {Headline, Url, Published};
    })""",
    '[data-component="Section"]')

    rand_delay(2)


if not secondo:
    shot_grabber(0,'https://www.abc.net.au/news/alex-palmer/8752082','ABC Alex Palmer', 
    'ABC','https://www.abc.net.au', "alex_palmer",
    """
    Array.from(document.querySelectorAll('[data-component="DetailCard"]'), el => {
    let Headline = el.querySelector('h3').innerText;

    let Url = el.querySelector('[data-component="Link"]')['href']
    let Published = el.querySelector('time').getAttribute("datetime")

    return {Headline, Url, Published};
    })""",
    '[data-component="Section"]')

    rand_delay(2)

if secondo:
    shot_grabber(0,'https://www.abc.net.au/news/simon-elvery/5449816','ABC Simon Elvery', 
    'ABC','https://www.abc.net.au', "simon_elvery",
    """
    Array.from(document.querySelectorAll('[data-component="DetailCard"]'), el => {
    let Headline = el.querySelector('h3').innerText;

    let Url = el.querySelector('[data-component="Link"]')['href']
    let Published = el.querySelector('time').getAttribute("datetime")

    return {Headline, Url, Published};
    })""",
    '[data-component="Section"]')

    rand_delay(2)

if not secondo:
    shot_grabber(0,'https://www.abc.net.au/news/georgina-piper/9255388','Georgina Piper', 
    'ABC','https://www.abc.net.au', "georgina_piper",
    """
    Array.from(document.querySelectorAll('[data-component="DetailCard"]'), el => {
    let Headline = el.querySelector('h3').innerText;

    let Url = el.querySelector('[data-component="Link"]')['href']
    let Published = el.querySelector('time').getAttribute("datetime")

    return {Headline, Url, Published};
    })""",
    '[data-component="Section"]')

    rand_delay(2)

# if not secondo:
#     shot_grabber(0,'https://www.abc.net.au/news/colin-gourlay/5359172','Colin Gourlay', 
#     'ABC','https://www.abc.net.au', "colin_gourlay",
#     """
#     Array.from(document.querySelectorAll('[data-component="DetailCard"]'), el => {
#     let Headline = el.querySelector('h3').innerText;

#     let Url = el.querySelector('[data-component="Link"]')['href']
#     let Published = el.querySelector('time').getAttribute("datetime")

#     return {Headline, Url, Published};
#     })""",
#     '[data-component="Section"]')

#     rand_delay(2)


if secondo:
    shot_grabber(0,'https://www.crikey.com.au/author/rachel-withers/','Rachel Withers', 
    'Crikey','https://www.crikey.com.au', "rachel_withers",
    """
    Array.from(document.querySelectorAll('.article__panel'), el => {
    let Headline = el.querySelector('h2').innerText;
    let Url = el.querySelector('a')['href']
    let Published = el.querySelector('.date').innerText
    return {Headline, Url, Published};
    })""",
    '.container_12')

    rand_delay(2)


if not secondo:
    shot_grabber(0,'https://www.crikey.com.au/author/cam-wilson/','Cam Wilson', 
    'Crikey','https://www.crikey.com.au', "cam_wilson",
    """
    Array.from(document.querySelectorAll('.article__panel'), el => {
    let Headline = el.querySelector('h2').innerText;
    let Url = el.querySelector('a')['href']
    let Published = el.querySelector('.date').innerText
    return {Headline, Url, Published};
    })""",
    '.container_12')

    rand_delay(2)


