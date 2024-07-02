import asyncio
from datetime import datetime, timedelta

import aiohttp
import feedparser

rss_url = "https://www.mk.co.kr/rss/40300001/"


async def fetch_rss_feed():
    async with aiohttp.ClientSession() as session:
        async with session.get(rss_url, ssl=False) as response:
            response.raise_for_status()
            feed_content = await response.text()

            # feedparser로 파싱
            feed = feedparser.parse(feed_content)
            articles = []

            for entry in feed.entries:
                title = entry.title if "title" in entry else "No title"
                link = entry.link if "link" in entry else "No link"
                published = entry.published if "published" in entry else "N/A"
                timestamp = datetime.now()
                articles.append(
                    {
                        "title": title,
                        "link": link,
                        "published": published,
                        "timestamp": timestamp,
                    }
                )

            return articles


async def run_crawl_and_store():
    articles = await fetch_rss_feed()
    if articles:
        for article in articles:
            print(article)
    else:
        print("No articles found.")


async def schedule_task():
    while True:
        now = datetime.now()
        target_time = now.replace(hour=22, minute=54, second=0, microsecond=0)
        if now >= target_time:
            target_time += timedelta(days=1)
        delay = (target_time - now).total_seconds()
        await asyncio.sleep(delay)
        await run_crawl_and_store()
