import os
import requests
import json
from dotenv import load_dotenv, find_dotenv
from newspaper import Article
from newspaper import Config
from datetime import datetime
import nltk
import logging

TODAYS_DATE = datetime.now().strftime("%b %d, %Y")
def get_top_news(news_api_key, todays_date):
    news_information = dict()
    # we only want science news in english
    params = {
        "category": "science",
        "language": "en",
        "apiKey": news_api_key
    }
    try:
        response = requests.get("https://newsapi.org/v2/top-headlines", params=params)
        
    except Exception as e:
        logging.error(f"Error fetching news: {e}")
        return news_information
    
    news_articles = response.json()['articles']
    user_agent = """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) """  # noqa
    config = Config()
    config.browser_user_agent = user_agent
    config.request_timeout = 10

    for article_info in news_articles:
        try:
            article = Article(article_info['url'], config=config)
            article.download()
            article.parse()
        except Exception as e:
            logging.error(f"Error fetching article: {e}")
            continue
        article.nlp()
        summary = article.summary  # noqa
        news_information[article_info["source"]["name"]] = {"title": article_info["title"], "summary": summary, "url": article_info["url"], "date": f"{todays_date}"}  # noqa
    return news_information


def write_news_to_file(news_information, todays_date):
    dir_path = "hestia/news/news_summary"
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, f"news_summary {todays_date}.txt")
    try:
        with open(file_path, "w") as outfile:
            json.dump(news_information, outfile, indent=4)
    except IOError as e:
        logging.error(f"I/O error({e.errno}): {e.strerror}")


def news_today():
    load_dotenv(find_dotenv(r"path to env variable"))
    news_api_key = os.getenv("NEWS_API_KEY")
    nltk.download('punkt', quiet=True)
    news_information = get_top_news(news_api_key, TODAYS_DATE)
    write_news_to_file(news_information, TODAYS_DATE)
    
    
