import asyncio
from datetime import datetime, timedelta

import aiohttp
import feedparser
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.model.article_publisher import Publisher
from app.service.simple_article_service import generate_simple_article


async def fetch_rss_feed(rss_url, publisher_name):
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
                        "publisher": publisher_name,
                    }
                )

            return articles


async def fetch_and_store_all_publisher_feeds():
    publisher_list = Publisher.list_publishers()
    all_articles = []

    for pub in publisher_list:
        if pub.info.rss is not None:
            rss_url = pub.info.rss
            articles = await fetch_rss_feed(rss_url, pub.name)
            all_articles.extend(articles)

    return all_articles


async def run_crawl_and_store(session: AsyncSession):
    articles = await fetch_and_store_all_publisher_feeds()
    if articles:
        tasks = [
            generate_simple_article(
                publisher=article["publisher"], url=article["link"], session=session
            )
            for article in articles
        ]
        await asyncio.gather(*tasks)
    else:
        print("No articles found.")


async def schedule_task():
    while True:
        now = datetime.now()
        target_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
        if now >= target_time:
            target_time += timedelta(days=1)
        delay = (target_time - now).total_seconds()
        await asyncio.sleep(delay)

        async with get_db_session() as session:  # pylint: disable=not-async-context-manager
            await run_crawl_and_store(session)
