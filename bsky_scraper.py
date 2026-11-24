import datetime
import json
import re

import feedparser
import pandas as pd
import pytz
import requests
from dateutil import tz
from feedgen.feed import FeedGenerator
from sudulunu.helpers import dumper

import pathlib
import os

pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

today = datetime.datetime.now()
scrape_time = today.astimezone(pytz.timezone("Australia/Brisbane"))
format_scrape_time = datetime.datetime.strftime(scrape_time, "%Y_%m_%d_%H")

OUT_PATH = "bsky_combined"
STATE_FILE = f"scraped/{OUT_PATH}/state.json"

HANDLES = [
    "pbump.com",
    "zackbeauchamp.bsky.social",
    "gelliottmorris.com",
    "taniel.bsky.social",
    "chrislhayes.bsky.social",
    "adamserwer.bsky.social",
    "jamellebouie.net",
]

# bsky.app blocks requests with no User-Agent
HEADERS = {"User-Agent": "Mozilla/5.0"}

INVALID_XML_RE = re.compile(
    r"[^\x09\x0A\x0D\x20-퟿-�\U00010000-\U0010FFFF]"
)


def clean_xml_text(text):
    if isinstance(text, str):
        return INVALID_XML_RE.sub("", text)
    return text


def make_path(out_path):
    already_there = os.listdir("scraped")
    if out_path not in already_there:
        os.mkdir(f"scraped/{out_path}")


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def fetch_handle_rss(handle):
    r = requests.get(f"https://bsky.app/profile/{handle}/rss", headers=HEADERS, timeout=30)
    r.raise_for_status()
    return feedparser.parse(r.content)


def quoted_text_for_uris(uris):
    """Resolve at:// post uris via the public AppView and pull out any quoted post's author/text."""
    quotes = {}
    for i in range(0, len(uris), 25):
        batch = uris[i:i + 25]
        r = requests.get(
            "https://public.api.bsky.app/xrpc/app.bsky.feed.getPosts",
            params=[("uris", u) for u in batch],
            headers=HEADERS,
            timeout=30,
        )
        if not r.ok:
            continue

        for post in r.json().get("posts", []):
            embed = post.get("embed") or {}

            record = None
            if embed.get("$type") == "app.bsky.embed.record#view":
                record = embed.get("record")
            elif embed.get("$type") == "app.bsky.embed.recordWithMedia#view":
                record = (embed.get("record") or {}).get("record")

            if not record or record.get("$type") != "app.bsky.embed.record#viewRecord":
                continue

            quoted_text = (record.get("value") or {}).get("text")
            author = record.get("author") or {}

            if quoted_text:
                quotes[post["uri"]] = {
                    "handle": author.get("handle", ""),
                    "text": quoted_text,
                }
    return quotes


def collect_new_posts():
    state = load_state()
    new_entries_by_handle = {}

    for handle in HANDLES:
        print(f"Checking {handle}")
        try:
            feed = fetch_handle_rss(handle)
        except Exception as e:
            print(f"Failed to fetch {handle}: {e}")
            continue

        last_seen = state.get(handle)
        new_entries = []
        for entry in feed.entries:
            if entry.get("id") == last_seen:
                break
            new_entries.append(entry)

        if new_entries:
            state[handle] = feed.entries[0].get("id")

        new_entries_by_handle[handle] = new_entries

    save_state(state)
    return new_entries_by_handle


def build_rows(new_entries_by_handle):
    all_uris = [
        entry.get("id")
        for entries in new_entries_by_handle.values()
        for entry in entries
    ]
    quotes = quoted_text_for_uris(all_uris) if all_uris else {}

    rows = []
    for handle, entries in new_entries_by_handle.items():
        for entry in entries:
            uri = entry.get("id")
            quote = quotes.get(uri)

            text = entry.get("summary", "")
            if quote:
                text = f"{text}\n\nQuoting @{quote['handle']}: {quote['text']}"

            published = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)

            rows.append({
                "Who": handle,
                "Url": entry.get("link"),
                "Headline": text,
                "Published": published.strftime("%Y_%m_%d_%H"),
                "_sort": published,
            })

    return rows


def make_feed(frame, out_path):
    entries = frame.copy()
    entries["Published"] = pd.to_datetime(entries["Published"], format="%Y_%m_%d_%H").dt.tz_localize(tz.tzlocal())

    fg = FeedGenerator()
    fg.id("https://bsky.app")
    fg.title("Bluesky updates")
    fg.author({"name": "Bluesky combined"})
    fg.description("Combined updates from followed Bluesky accounts, since the last run")
    fg.link(href="https://bsky.app", rel="self")
    fg.language("en")

    for ind in entries.index:
        fe = fg.add_entry()
        fe.id(entries["Url"][ind])
        fe.title(f"{entries['Who'][ind]}: {entries['Headline'][ind][:80]}")
        fe.link(href=entries["Url"][ind])
        fe.description(entries["Headline"][ind])
        fe.published(entries["Published"][ind])

    fg.rss_file(f"scraped/{out_path}/rss.xml")


def run():
    make_path(OUT_PATH)

    new_entries_by_handle = collect_new_posts()
    rows = build_rows(new_entries_by_handle)

    datah = pd.DataFrame(rows, columns=["Who", "Url", "Headline", "Published", "_sort"])

    if not datah.empty:
        datah.drop_duplicates(subset="Url", inplace=True)
        datah.sort_values(by="_sort", ascending=False, inplace=True)
        datah.drop(columns="_sort", inplace=True)

        for col in ["Who", "Url", "Headline"]:
            datah[col] = datah[col].apply(clean_xml_text)
    else:
        datah = datah[["Who", "Url", "Headline", "Published"]]

    dumper(f"scraped/{OUT_PATH}", "latest", datah)
    make_feed(datah, OUT_PATH)

    print(f"{len(datah)} new post(s) since last run")


run()
