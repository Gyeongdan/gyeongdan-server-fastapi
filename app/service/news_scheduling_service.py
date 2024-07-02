import asyncio
from datetime import datetime, timedelta

import aiohttp
import feedparser

from app.model.article_publisher import Publisher


# Helper function to fetch RSS feed and parse articles
async def fetch_rss_feed(rss_url):
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


# 모든 발행사의 RSS 피드를 가져와서 저장하는 함수
async def fetch_and_store_all_publisher_feeds():
    publisher_list = Publisher.list_publishers()
    all_articles = []

    for pub in publisher_list:
        if pub.info.rss is not None:
            rss_url = pub.info.rss
            articles = await fetch_rss_feed(rss_url)
            all_articles.extend(articles)

    return all_articles


# 모든 발행사의 RSS 피드를 가져와서 저장하는 함수를 실행하는 함수
async def run_crawl_and_store():
    articles = await fetch_and_store_all_publisher_feeds()
    if articles:
        for article in articles:
            link = article.get("link")
            title = article.get("title")

            print(f"Title: {title}")
            print(f"Link: {link}")

    else:
        print("No articles found.")


# Scheduling function to run at 9 AM every day
async def schedule_task():
    while True:
        now = datetime.now()
        target_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
        if now >= target_time:
            target_time += timedelta(days=1)
        delay = (target_time - now).total_seconds()
        await asyncio.sleep(delay)
        await run_crawl_and_store()


# Main function
