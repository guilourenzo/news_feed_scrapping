import feedparser
import pandas as pd
import sqlite3
# import schedule
import time
from dateutil import parser as date_parser

# Function to fetch and parse RSS feed with filters
def fetch_rss_feed(url, keywords=None, start_date=None):
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries:
        if keywords:
            if not any(keyword.lower() in (entry.title + ' ' + entry.description).lower() for keyword in keywords):
                continue
        
        if start_date:
            try:
                published_date = date_parser.parse(entry.published).replace(tzinfo=None)
            except Exception as e:
                print(f"Error parsing date: {e}")
                continue

            if published_date < start_date:
                continue
        
        articles.append({
            'title': entry.title,
            'description': entry.description,
            'link': entry.link,
            'published': entry.published
        })
    return pd.DataFrame(articles)

# Simple classification function based on keywords
def classify_article(title, description):
    finance_keywords = ['stock', 'market', 'finance', 'investment', 'economy']
    content = title + ' ' + description
    if any(keyword in content.lower() for keyword in finance_keywords):
        return 'Finance'
    else:
        return 'News'

# Function to initialize the database
def initialize_db():
    conn = sqlite3.connect('db/articles.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            title TEXT,
            description TEXT,
            link TEXT PRIMARY KEY,
            published TEXT,
            category TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Function to save new articles to the database
def save_articles_to_db(articles):
    conn = sqlite3.connect('db/articles.db')
    cursor = conn.cursor()
    
    for _, article in articles.iterrows():
        try:
            cursor.execute('''
                INSERT INTO articles (title, description, link, published, category) VALUES (?, ?, ?, ?, ?)
            ''', (article['title'], article['description'], article['link'], article['published'], article['category']))
        except sqlite3.IntegrityError:
            # Skip duplicates
            continue
    
    conn.commit()
    conn.close()

# Function to fetch, classify, and save new articles
def fetch_and_update_articles():
    g1_rss_url = 'https://g1.globo.com/rss/g1/'
    infomoney_rss_url = 'https://www.infomoney.com.br/feed/'
    
    # Keywords and date filter
    keywords = ['economy', 'investment', 'market']
    start_date = date_parser.parse('01 Jan 2024').replace(tzinfo=None)
    
    g1_articles = fetch_rss_feed(g1_rss_url, keywords, start_date)
    infomoney_articles = fetch_rss_feed(infomoney_rss_url, keywords, start_date)
    
    all_articles = pd.concat([g1_articles, infomoney_articles], ignore_index=True)
    all_articles['category'] = all_articles.apply(lambda x: classify_article(x['title'], x['description']), axis=1)
    
    save_articles_to_db(all_articles)
    print(f'Updated articles at {time.strftime("%Y-%m-%d %H:%M:%S")}')

# Initialize the database
initialize_db()