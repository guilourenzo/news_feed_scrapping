import feedparser
import pandas as pd
from dateutil import parser as date_parser

class RSSFeedParser:
    def __init__(self, url, keywords=None, start_date=None):
        self.url = url
        self.keywords = keywords
        self.start_date = date_parser.parse(start_date).replace(tzinfo=None) if start_date else None

    def fetch_rss_feed(self):
        feed = feedparser.parse(self.url)
        articles = []
        for entry in feed.entries:
            if self.keywords:
                if not any(keyword.lower() in (entry.title + ' ' + entry.description).lower() for keyword in self.keywords):
                    continue

            if self.start_date:
                try:
                    published_date = date_parser.parse(entry.published).replace(tzinfo=None)
                except Exception as e:
                    print(f"Error parsing date: {e}")
                    continue

                if published_date < self.start_date:
                    continue

            articles.append({
                'title': entry.title,
                'description': entry.description,
                'link': entry.link,
                'published': entry.published
            })
        return pd.DataFrame(articles)
