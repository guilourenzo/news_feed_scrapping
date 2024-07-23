# import os
import json
import pandas as pd

# import schedule
import time
from dateutil import parser as date_parser
from rss_feed_parser import RSSFeedParser
from article_classifier import ArticleClassifier
from db.database_handler import DatabaseHandler


class RSSFeedUpdater:
    def __init__(self, db_handler, classifiers, feeds):
        self.db_handler = db_handler
        self.classifiers = classifiers
        self.feeds = feeds

    def fetch_and_update_articles(self):
        all_articles = pd.DataFrame()
        for feed in self.feeds:
            parser = RSSFeedParser(feed['url'], feed.get('keywords'), feed.get('start_date'))
            articles = parser.fetch_rss_feed()
            classifier = self.classifiers[feed['classifier']]
            if not articles.empty:
                articles['category'] = articles.apply(lambda x: classifier.classify_article(x['title'], x['description']), axis=1)
                all_articles = pd.concat([all_articles, articles], ignore_index=True)
        
        self.db_handler.save_articles_to_db(all_articles)
        print(f'Updated articles at {time.strftime("%Y-%m-%d %H:%M:%S")}')
        return all_articles


def main():
    # Load configuration
    with open("news_scrapping/config.json") as config_file:
        config = json.load(config_file)

    # Initialize database handler
    db_handler = DatabaseHandler(config["db_location"])

    # Initialize classifiers
    article_classifier = ArticleClassifier()

    # Define feeds
    feeds = config["feeds"]

    # Initialize feed updater
    classifiers = {
        "finance": article_classifier,
        "politics": article_classifier,
        "sports": article_classifier,
        "entertainment": article_classifier,
        "technology": article_classifier,
    }
    feed_updater = RSSFeedUpdater(db_handler, classifiers, feeds)
    feeds_found = feed_updater.fetch_and_update_articles()
    # print(feeds_found)
    db_handler.close()
    # Schedule the script to run at specified intervals
    # interval_hours = config['schedule']['interval_hours']
    # schedule.every(interval_hours).hours.do(feed_updater.fetch_and_update_articles)

    # # Run the scheduler
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)


if __name__ == "__main__":
    main()
