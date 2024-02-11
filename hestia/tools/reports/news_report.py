import os
import requests
from dotenv import load_dotenv
from newspaper import Article
from newspaper import Config
from datetime import datetime
import nltk
from typing import List
from hestia.lib.hestia_logger import logger
from hestia.llm.llama_chat_completion import load_prompt, chat_completion, load_prompt_txt
from hestia.text_to_speech.speech import TextToSpeechSystem
from hestia.tools.reports.base_report_generator import BaseReportGenerator
from hestia.config.config import cfg


# hestia/tools/news/newsapi.py
class NewsReport(BaseReportGenerator):
    """A class to represent a NewsReport.
    Attributes:
        DIR_PATH: The path to the directory where the news report is stored.
        NEWS_API_KEY: The API key for the News API."""
    NEWS_API_KEY = cfg.NEWS_API_KEY
    
    def __init__(self):
        """Initialize the NewsReport.
        Attributes:
            todays_date: The date of the news report.
            news_summary_path: The path to the news summary.
            simplified_news_path: The path to the simplified news.
            news_summary_speech_path: The path to the news summary speech."""
        self.todays_date = datetime.now().strftime("%b %d, %Y")
        self.news_summary_path = os.path.join(cfg.REPORT_SUMMARY_PATH, f"news_summary {self.todays_date}.txt")
        nltk.download('punkt', quiet=True)
        
    def read_file(self, file_path: str):
        """Read a file.
        Args:
            file_path: The path to the file.
        Returns:
            str: The content of the file."""
        with open(file_path, "r") as f:
            return f.read()
        
    def write_file(self, file_path: str, content: str):
        """Write to a file.
        Args:
            file_path: The path to the file.
            content: The content to write to the file.
        Returns:
            str: The content of the file."""
        with open(file_path, "w") as f:
            f.write(content)
            
    def encode_to_ascii(self, text: str):
        """Encode text to ascii.
        Args:
            text: The text to encode.
        Returns:
            str: The encoded text."""
        return text.encode('ascii', 'ignore').decode('ascii')


        
        
    def get_news_params(self, news_api_key: str)->dict:
        """Get the parameters for the news request.
        Args:
            news_api_key: The API key for the News API.
        Returns:
            dict: The parameters for the news request."""
        return {
            "category": "science",
            "language": "en",
            "apiKey": news_api_key
        }
        
    def make_news_request(self, params: dict):
        """Make a news request.
        Args:
            params: The parameters for the news request.
        Returns:
            requests.Response: The response from the news request."""
        try:
            return requests.get("https://newsapi.org/v2/top-headlines", params=params)
        except Exception as e:
            logger.error(f"Error making news request: {e}")
            raise
        
    def parse_news_response(self, response):
        """Parse the news response.
        Args:
            response: The response from the news request.
        Returns:
            list: The news articles."""
        return response.json()['articles']  
    
    def get_config(self)->Config:
        """Get the config for the news request."""
        user_agent = """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) """
        config = Config()
        config.browser_user_agent = user_agent
        config.request_timeout = 10
        return config
    
    def download_and_parse_article(self, article_info, config)->Article:
        """Download and parse the article.
        Args:
            article_info: The information about the article.
            config: The config for the news request.
        Returns:
            Article: The article."""
        article = Article(article_info['url'], config=config)
        article.download()
        article.parse()
        return article
    
    def get_article_info(self, article_info: dict, article: Article)->dict:
        """Get the article information.
        Args:
            article_info: The information about the article.
            article: The article.
        Returns:
            dict: The article information."""
        article.nlp()
        summary = self.encode_to_ascii(article.summary.replace("\n", ""))
        title = self.encode_to_ascii(article_info["title"])
        return {"title": title, "summary": summary, "url": article_info["url"], "date": f"{self.todays_date}"}
    
    def get_information(self, news_api_key: str)->dict:
        """Get the news information.
        Args:
            news_api_key: The API key for the News API.
        Returns:
            dict: The news information."""
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
    

    def parse_information(self)->str:
        """Parse the news information."""
        news_information = self.get_information(cfg.NEWS_API_KEY)
        news_information = {k: v for k, v in news_information.items() if k != "[Removed]"}
        for key, value in news_information.items():
            value.pop("url", None)
            value.pop("date", None)
            value["title"] = self.encode_to_ascii(value.get("title", ""))
            value["summary"] = self.encode_to_ascii(value.get("summary", ""))
        news_information = [value["title"] + "." for value in news_information.values()]
        return "\n".join(news_information)
        

            
            
    def generate_report_summary(self):
        """Generate the news report summary."""
        news = self.parse_information()
        news_prompt = load_prompt_txt(prompt_name="news_debrief")
        news_summary = chat_completion(system_prompt=news_prompt, user_prompt=f"The news for {self.todays_date}:\n\n{news}")
        self.write_file(self.news_summary_path, news_summary)


    def convert_summary_to_audio(self):
        """Convert the news summary to audio using text to speech."""
        news = self.read_file(self.news_summary_path)
        tts = TextToSpeechSystem()
        if news is None:
            return
        tts.convert_text_to_speech(
            text=news,
            output_dir="hestia/text_to_speech/outputs/news_report",
            output_filename=f"{self.todays_date}news_report"
        )
    
    def generate_report(self):
        """Generate the news report."""
        self.generate_report_summary()
        self.convert_summary_to_audio()
    