import sqlite3
import pandas as pd

class DatabaseHandler:
    def __init__(self, db_name='articles.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.initialize_db()

    def initialize_db(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                title TEXT,
                description TEXT,
                link TEXT PRIMARY KEY,
                published TEXT,
                category TEXT
            )
        ''')
        self.conn.commit()

    def save_articles_to_db(self, articles):
        for _, article in articles.iterrows():
            try:
                self.cursor.execute('''
                    INSERT INTO articles (title, description, link, published, category) VALUES (?, ?, ?, ?, ?)
                ''', (article['title'], article['description'], article['link'], article['published'], article['category']))
            except sqlite3.IntegrityError:
                # Skip duplicates
                continue
        self.conn.commit()

    def close(self):
        self.conn.close()
