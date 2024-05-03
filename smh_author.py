from playwright.sync_api import sync_playwright
import dateparser
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

def dumper(path, name, frame):
    with open(f'{path}/{name}.csv', 'w') as f:
        frame.to_csv(f, index=False, header=True)

def rand_delay(num):
  import random 
  import time 
  rando = random.random() * num
  print(rando)
  time.sleep(rando)

def shot_grabber(urlo, who,site, siteurl, out_path,  javascript_code, awaito):
    tries = 0
    with sync_playwright() as p:
        try:
            # print("Trying")
            browser = p.firefox.launch()
            # browser = p.chromium.launch()

            context = browser.new_context()

            page = context.new_page()
            print(page)

            # stealth_sync(page)

            print("Going")

            page.goto(urlo)

            print('Before waiting')
            waiting_around = page.locator(awaito)
            waiting_around.wait_for()
            print("After waiting")

            resulto = page.evaluate(javascript_code)

            print("Resulto: ", resulto)

            browser.close()

            frame = pd.DataFrame.from_records(resulto)

            frame = frame[:10]

            frame['Who'] = who

            frame['Site'] = site

            frame['Siteurl'] = siteurl

            frame['scraped_datetime']= format_scrape_time 

            frame = frame[['Who', 'scraped_datetime', 'Headline', 'Url', 'Site', 'Siteurl', 'Published']]

            frame['Published']= pd.to_datetime(frame['Published'], utc=True)
            frame['Published'] = frame['Published'].dt.strftime("%Y_%m_%d_%H")

            old = pd.read_csv('data/combined.csv')

            tog = pd.concat([frame, old])
            tog.drop_duplicates(subset=['Headline','Url'], inplace=True)

            dumper('data', 'combined', tog)

            dumper(f'data/{out_path}', f"{format_scrape_time }", frame)

            return frame 

        except Exception as e:
            tries += 1
            print("Tries: ", tries)
            browser.close()
            print(e)
            rand_delay(5)
            if tries <= 3:
            # if e == 'Timeout 30000ms exceeded.' and tries <= 3:
                print("Trying again")
                shot_grabber(urlo, who,site, siteurl, out_path,  javascript_code, awaito)





# print("Scraping Sean Kelly")

# try:
#     smh = shot_grabber('https://www.smh.com.au/by/sean-kelly-h1d26a','Sean Kelly', 
#                        'SMH','https://www.smh.com.au/', "sean_kelly",
#         """
#         Array.from(document.querySelectorAll('._3SZUs,.X3yYQ'), el => {
#         let Headline = el.querySelector('h3').innerText;
#         let Url = el.querySelector('a')['href']
#         let Published = el.querySelector('._2_zR-')['dateTime']
#         return {Headline, Url, Published};
#         })""",
#         '._2VCps _2GpEY')
    
# except Exception as e:
#     print(e)



# print("Scraping Reuters")

# try:
#     smh = shot_grabber('https://www.reuters.com/graphics/','Reuters Graphics', 
#                        'Reuters','https://www.reuters.com', "reuters",
#         """
# Array.from(document.querySelectorAll('article.svelte-11dknnx,div.hero-row'), el => {

# let Headline = el.querySelector('h2,h3').innerText;
# let Url = el.querySelector('a')['href']
# let Published = el.querySelector('small').innerText;
# return {Headline, Url, Published};
# })""",
#         '.hero-row clearfix')
    
# except Exception as e:
#     print(e)

print("Scraping SCMP")

try:
    smh = shot_grabber('https://www.scmp.com/infographic/#recentproj','SCMP Graphics', 
                       'SCMP','https://www.scmp.com', "scmp",
        """
Array.from(document.querySelectorAll('#half0'), el => {
let Headline = el.querySelector('h2').innerText;
let Url = el.querySelector('a')['href']
let Published = el.querySelector('.feed-date').innerText.split("|")
Published = Published.pop().trim()

return {Headline, Url, Published};
})""",
        '#allFeature')
    
except Exception as e:
    print(e)


# Published = Published.slice(-1)
# let Url = el.querySelector('a')['href']
# return {Headline, Url};

