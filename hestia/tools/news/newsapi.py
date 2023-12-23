import os
import requests
import json
from dotenv import load_dotenv, find_dotenv
from newspaper import Article
from newspaper import Config
from datetime import datetime
import nltk
import logging
from hestia.llm.llama_chat_completion import load_news_prompt, chat_completion
from hestia.text_to_speech.speech import TextToSpeechSystem


TODAYS_DATE = datetime.now().strftime("%b %d, %Y")
DIR_PATH = "hestia/tools/news/news_summary"
NEWS_SUMMARY_PATH = os.path.join(DIR_PATH, f"news_summary {TODAYS_DATE}.txt")
CLEAN_NEWS_PATH = os.path.join(DIR_PATH, f"{TODAYS_DATE}clean.txt")
SIMPLIFIED_NEWS_PATH = os.path.join(DIR_PATH, f"{TODAYS_DATE}simplified.txt")
NEWS_SUMMARY_SPEECH_PATH = os.path.join(DIR_PATH, f"{TODAYS_DATE}summary.txt")

def get_top_news(news_api_key, todays_date):
    news_information = dict()
    params = get_news_params(news_api_key)
    response = make_news_request(params)
    news_articles = parse_news_response(response)
    config = get_config()

    for article_info in news_articles:
        try:
            article = download_and_parse_article(article_info, config)
        except Exception as e:
            logging.error(f"Error fetching article: {e}")
            continue
        news_information[article_info["source"]["name"]] = get_article_info(article_info, article, todays_date)
    return news_information

def get_news_params(news_api_key):
    return {
        "category": "science",
        "language": "en",
        "apiKey": news_api_key
    }

def make_news_request(params):
    try:
        return requests.get("https://newsapi.org/v2/top-headlines", params=params)
    except Exception as e:
        logging.error(f"Error fetching news: {e}")
        raise

def parse_news_response(response):
    return response.json()['articles']

def get_config():
    user_agent = """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) """  # noqa
    config = Config()
    config.browser_user_agent = user_agent
    config.request_timeout = 10
    return config

def download_and_parse_article(article_info, config):
    article = Article(article_info['url'], config=config)
    article.download()
    article.parse()
    return article

def get_article_info(article_info, article, todays_date):
    article.nlp()
    summary = article.summary  # noqa
    return {"title": article_info["title"], "summary": summary, "url": article_info["url"], "date": f"{todays_date}"}  # noqa

def write_news_to_file(news_information, todays_date):
    dir_path = "hestia/tools/news/news_summary"
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, f"news_summary {todays_date}.txt")
    try:
        with open(file_path, "w") as outfile:
            json.dump(news_information, outfile, indent=4)
    except IOError as e:
        logging.error(f"I/O error({e.errno}): {e.strerror}")

def read_json_file(path):
    try:
        with open(path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File not found: {path}")
    except json.JSONDecodeError:
        print(f"Could not decode JSON from file: {path}")

def write_json_file(path, data):
    try:
        with open(path, "w") as file:
            json.dump(data, file, indent=4)
    except FileNotFoundError:
        print(f"File not found: {path}")

def read_file(path):
    try:
        with open(path, "r") as file:
            return file.read()
    except FileNotFoundError:
        print(f"File not found: {path}")

def write_file(path, data):
    try:
        with open(path, "w") as file:
            file.write(data)
    except FileNotFoundError:
        print(f"File not found: {path}")

def clean_news_summary():
    news_summary = read_json_file(NEWS_SUMMARY_PATH)
    if news_summary is None:
        return

    news_summary = {k: v for k, v in news_summary.items() if k != "[Removed]"}

    for key, value in news_summary.items():
        value.pop("url", None)
        value.pop("date", None)

        title = value.get("title", "").encode('ascii', 'ignore').decode('ascii')
        value["title"] = title

        summary = value.get("summary", "").replace("\n", "").encode('ascii', 'ignore').decode('ascii')
        value["summary"] = summary

    write_json_file(CLEAN_NEWS_PATH, news_summary)

def extract_simplified_news():
    news = read_json_file(CLEAN_NEWS_PATH)
    if news is None:
        return

    news = [value["title"] + "." for value in news.values()]
    write_file(SIMPLIFIED_NEWS_PATH, "\n".join(news))

def generate_news_summary():
    news_prompt = load_news_prompt()
    news = read_file(SIMPLIFIED_NEWS_PATH)
    if news is None:
        return

    news_summary = chat_completion(news_prompt, news)["choices"][0]["message"]["content"]
    write_file(NEWS_SUMMARY_SPEECH_PATH, news_summary)

def convert_news_summary_to_speech():
    tts = TextToSpeechSystem()
    news_summary = read_file(NEWS_SUMMARY_SPEECH_PATH)
                                                                                                                                                                                              
def prepare_news_summary():
    load_dotenv(find_dotenv(r"path to env variable"))
    news_api_key = os.getenv("NEWS_API_KEY")
    nltk.download('punkt', quiet=True)
    news_information = get_top_news(news_api_key, TODAYS_DATE)
    write_news_to_file(news_information, TODAYS_DATE)
    clean_news_summary()
    extract_simplified_news()
    generate_news_summary()
    print("Done")
    
    
