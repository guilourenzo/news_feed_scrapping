import json
import pandas as pd
import sqlite3
import streamlit as st
from datetime import datetime
from bs4 import BeautifulSoup
from db.database_handler import DatabaseHandler
from rss_feed_parser import RSSFeedParser
from article_classifier import ArticleClassifier
from rss_feed_updater import RSSFeedUpdater


# Load the configuration file
def load_config(file_path="news_scrapping/config.json"):
    with open(file_path, "r") as file:
        config = json.load(file)
    return config


# Save the configuration file
def save_config(config, file_path="news_scrapping/config.json"):
    with open(file_path, "w") as file:
        json.dump(config, file, indent=4)


# Load articles from the database
def load_articles(db_location="news_scrapping/db/articles.db"):
    conn = sqlite3.connect(db_location)
    query = "SELECT * FROM articles"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


# Extract the caption image URL and clean the description
def extract_image_and_clean_description(description):
    soup = BeautifulSoup(description, "html.parser")
    img_tag = soup.find("img")
    if img_tag:
        image_url = img_tag["src"]
        img_tag.extract()
    else:
        image_url = None
    cleaned_description = soup.get_text()
    return image_url, cleaned_description


# Initialize Streamlit app
st.title("RSS News Manager")

# Sidebar for configuration
st.sidebar.title("Configuration")
config = load_config()

# Database location
st.sidebar.subheader("Database Location")
db_location = st.sidebar.text_input("Database Location", config["db_location"])
config["db_location"] = db_location

# Schedule interval
st.sidebar.subheader("Schedule Interval (Hours)")
interval_hours = st.sidebar.number_input(
    "Interval Hours", min_value=1, value=config["schedule"]["interval_hours"]
)
config["schedule"]["interval_hours"] = interval_hours

# RSS Feeds Management
st.sidebar.subheader("Manage RSS Feeds")
feeds = config["feeds"]
new_feed_url = st.sidebar.text_input("New Feed URL")
new_feed_keywords = st.sidebar.text_input("Keywords (comma-separated)")
new_feed_start_date = st.sidebar.date_input("Start Date", datetime.now())

# Add new feed
if st.sidebar.button("Add Feed"):
    if new_feed_url and new_feed_keywords and new_feed_start_date:
        new_feed = {
            "url": new_feed_url,
            "keywords": new_feed_keywords.split(","),
            "start_date": new_feed_start_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "classifier": st.sidebar.selectbox(
                "Classifier",
                [
                    "finance",
                    "politics",
                    "sports",
                    "entertainment",
                    "technology",
                    "health",
                ],
            ),
        }
        feeds.append(new_feed)
        config["feeds"] = feeds
        save_config(config)
        st.sidebar.success("Feed added successfully!")

# List existing feeds
st.sidebar.subheader("Existing Feeds")
for i, feed in enumerate(feeds):
    st.sidebar.markdown(f"**Feed {i + 1}:** {feed['url']}")
    st.sidebar.text(f"Keywords: {', '.join(feed['keywords'])}")
    st.sidebar.text(f"Start Date: {feed['start_date']}")
    st.sidebar.text(f"Classifier: {feed['classifier']}")

# Save configuration changes
if st.sidebar.button("Save Configuration"):
    save_config(config)
    st.sidebar.success("Configuration saved successfully!")

# Main content: Display articles
st.header("Extracted News Articles")
articles = load_articles(db_location)
if not articles.empty:
    for _, article in articles.iterrows():
        # Extract the image URL and clean the description
        image_url, cleaned_description = extract_image_and_clean_description(
            article["description"]
        )

        # Display the image if available
        if image_url:
            st.image(image_url)

        # Display the title and publication date
        st.subheader(article["title"])
        st.write(f"Published on: {article['published']}")

        # Display the cleaned description
        st.write(cleaned_description)

        # Display the link to the original article
        st.markdown(f"[News Source]({article['link']})")
else:
    st.write("No articles found.")

# Manual extraction button
st.header("Manual Extraction")
if st.button("Run Extraction Now"):
    # Initialize database handler
    db_handler = DatabaseHandler(db_location)

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
        "health": article_classifier,
    }
    feed_updater = RSSFeedUpdater(db_handler, classifiers, feeds)

    # Run the extraction
    feed_updater.fetch_and_update_articles()
    st.success("Extraction completed successfully!")

    # Refresh articles
    articles = load_articles(db_location)
    if not articles.empty:
        for _, article in articles.iterrows():
            # Extract the image URL and clean the description
            image_url, cleaned_description = extract_image_and_clean_description(
                article["description"]
            )

            # Display the image if available
            if image_url:
                st.image(image_url)

            # Display the title and publication date
            st.subheader(article["title"])
            st.write(f"Published on: {article['published']}")

            # Display the cleaned description
            st.write(cleaned_description)

            # Display the link to the original article
            st.markdown(f"[News Source]({article['link']})")
    else:
        st.write("No articles found.")
