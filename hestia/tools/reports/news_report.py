import os
import requests
from dotenv import load_dotenv
from newspaper import Article
from newspaper import Config
from datetime import datetime
import nltk
from hestia.lib.hestia_logger import HestiaLogger
from hestia.llm.llama_chat_completion import load_news_prompt, chat_completion
from hestia.text_to_speech.speech import TextToSpeechSystem
from hestia.tools.reports.base_report_generator import BaseReportGenerator
load_dotenv()



logger = HestiaLogger().logger
# hestia/tools/news/newsapi.py
class NewsReport(BaseReportGenerator):
    DIR_PATH = "hestia/tools/reports/news"
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    
    def __init__(self):
        self.todays_date = datetime.now().strftime("%b %d, %Y")
        self.news_summary_path = os.path.join(self.DIR_PATH, f"news_summary {self.todays_date}.txt")
        self.simplified_news_path = os.path.join(self.DIR_PATH, f"{self.todays_date}simplified.txt")
        self.news_summary_speech_path = os.path.join(self.DIR_PATH, f"{self.todays_date}summary.txt")
        nltk.download('punkt', quiet=True)
        
    def read_file(self, file_path):
        with open(file_path, "r") as f:
            return f.read()
        
    def write_file(self, file_path, content):
        with open(file_path, "w") as f:
            f.write(content)
            
    def encode_to_ascii(self, text):
        return text.encode('ascii', 'ignore').decode('ascii')


        
        
    def get_news_params(self, news_api_key):
        return {
            "category": "science",
            "language": "en",
            "apiKey": news_api_key
        }
        
    def make_news_request(self, params):
        try:
            return requests.get("https://newsapi.org/v2/top-headlines", params=params)
        except Exception as e:
            logger.error(f"Error making news request: {e}")
            raise
        
    def parse_news_response(self, response):
        return response.json()['articles']  
    
    def get_config(self):
        user_agent = """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) """
        config = Config()
        config.browser_user_agent = user_agent
        config.request_timeout = 10
        return config
    
    def download_and_parse_article(self, article_info, config):
        article = Article(article_info['url'], config=config)
        article.download()
        article.parse()
        return article
    
    def get_article_info(self, article_info, article):
        article.nlp()
        summary = self.encode_to_ascii(article.summary.replace("\n", ""))
        title = self.encode_to_ascii(article_info["title"])
        return {"title": title, "summary": summary, "url": article_info["url"], "date": f"{self.todays_date}"}
    
    def get_information(self, news_api_key):
        news_information = dict()
        params = self.get_news_params(news_api_key)
        response = self.make_news_request(params)
        news_articles = self.parse_news_response(response)
        config = self.get_config()
    
        for article_info in news_articles:
            try:
                article = self.download_and_parse_article(article_info, config)
            except Exception as e:
                logger.error(f"Error downloading and parsing article: {e}")
                continue
            news_information[article_info["source"]["name"]] = self.get_article_info(article_info, article)
        return news_information
    

    def parse_information(self):
        news_information = self.get_information(self.NEWS_API_KEY)
        news_information = {k: v for k, v in news_information.items() if k != "[Removed]"}
        for key, value in news_information.items():
            value.pop("url", None)
            value.pop("date", None)
            value["title"] = self.encode_to_ascii(value.get("title", ""))
            value["summary"] = self.encode_to_ascii(value.get("summary", ""))
        news_information = [value["title"] + "." for value in news_information.values()]
        self.write_file(self.simplified_news_path, "\n".join(news_information))

            
            
    def generate_report_summary(self):
        news = self.read_file(self.simplified_news_path)
        news_prompt = load_news_prompt()
        news_summary = chat_completion(sytem_prompt=news_prompt, user_prompt=news)
        news_summary = news_summary
        self.write_file(self.news_summary_path, news_summary)


    def convert_summary_to_audio(self):
        news = self.read_file(self.news_summary_path)
        tts = TextToSpeechSystem()
        if news is None:
            return
        tts.convert_text_to_speech_using_nlp(
            text=news,
            output_dir="hestia/text_to_speech/outputs/news_summary",
            output_filename=f"{self.todays_date}news_report"
        )