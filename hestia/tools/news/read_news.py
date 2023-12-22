from hestia.tools.news.newsapi import news_today, TODAYS_DATE
import json
from hestia.llm.llama_chat_completion import load_news_prompt, chat_completion
from hestia.text_to_speech.speech import TextToSpeechSystem

NEWS_SUMMARY_PATH = f"hestia/tools/news/news_summary/news_summary {TODAYS_DATE}.txt"
CLEAN_NEWS_PATH = f"hestia/tools/news/news_summary/ {TODAYS_DATE}clean.txt"
SIMPLIFIED_NEWS_PATH = f"hestia/tools/news/news_summary/ {TODAYS_DATE}simplified.txt"
NEWS_SUMMARY_SPEECH_PATH = f"hestia/tools/news/news_summary/ {TODAYS_DATE}summary.txt"

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
    if news_summary is None:
        return

    tts.convert_text_to_speech_using_nlp(
        text=news_summary,
        output_dir="hestia/text_to_speech/outputs/news_summary",
        output_filename=f"{TODAYS_DATE}summary"
    )

    
