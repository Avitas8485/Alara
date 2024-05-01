import os
import requests
from dotenv import load_dotenv
from newspaper import Article
from newspaper import Config
from datetime import datetime
import nltk
from typing import List
from alara.skills.skill_manager import Skill
from alara.tts.tts_engine import TTSEngine
from alara.lib.logger import logger
from alara.llm.llm_engine import LlmEngine
from alara.llm.llama_chat_completion import load_prompt_txt as load_prompt
load_dotenv()


class News(Skill):
    """A class to represent News.
    Attributes:
        DIR_PATH: The path to the directory where the news report is stored.
        NEWS_API_KEY: The API key for the News API."""
    
    def __init__(self):
        """Initialize the News.
        Attributes:
            todays_date: The date of the news report.
            news_summary_path: The path to the news summary.
            simplified_news_path: The path to the simplified news.
            news_summary_speech_path: The path to the news summary speech."""
        self.NEWS_API_KEY = os.getenv("NEWS_API_KEY", '')
        nltk.download('punkt', quiet=True)
        self.tts = TTSEngine.load_tts()
        self.llm = LlmEngine.load_llm()
        self.news_prompt = load_prompt("news_debrief")
        self.config = self.get_config()
    
    def get_config(self)->Config:
        """Get the config for the news request."""
        user_agent = """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) """
        config = Config()
        config.browser_user_agent = user_agent
        config.request_timeout = 10
        return config    
    
    def encode_to_ascii(self, text: str)->str:
        """Encode text to ascii.
        Args:
            text (str): The text to encode.
        Returns:
            str: The encoded text."""
        return text.encode('ascii', 'ignore').decode('ascii')
    
    def get_news_params(self, news_api_key: str)->dict:
        """Get the parameters for the news request.
        Args:
            news_api_key (str): The API key for the News API.
        Returns:
            dict: The parameters for the news request."""
        return {
            "language": "en",
            "apiKey": news_api_key
        }
    
    
    def make_news_request(self, params: dict)->requests.Response:
        """Make a news request.
        Args:
            params (dict): The parameters for the news request.
        Returns:
            requests.Response: The response from the news request."""
        try:
            return requests.get("https://newsapi.org/v2/top-headlines", params=params)
        except Exception as e:
            logger.error(f"Error making news request: {e}")
            raise
        
    def parse_news_response(self, response: requests.Response):
        """Parse the news response.
        Args:
            response (requests.Response): The response from the news request.
        Returns:
            list: The news articles."""
        articles = response.json()['articles']
        for article in articles:
            yield article
        
        
    
    
    
    def download_and_parse_article(self, article_info: dict):
        """Download and parse the article.
        Args:
            article_info: The information about the article.
            config: The config for the news request.
        Returns:
            Article: The article."""
        article = Article(article_info['url'], config=self.config)
        article.download()
        article.parse()
        article.nlp()
        symmary = article.summary.replace("\n", "")
        title = article_info["title"]
        yield f"{title}: {symmary}"
        
    
    
    def get_articles(self, params: dict):
        """Get the articles.
        Args:
            params (dict): The parameters for the news request.
        Returns:
            dict: The articles."""
        response = self.make_news_request(params)
        for article in self.parse_news_response(response):
            try:
                yield from self.download_and_parse_article(article)
            except Exception as e:
                logger.error(f"Error getting articles: {e}")
                continue
            
        
    
    @Skill.skill_feature
    def latest_news(self, tts: bool=True, summarize: bool=True) -> str:
        """Get the latest news.
        Args:
            tts (bool): Whether to use text to speech. Default is True.
            summarize (bool): Whether to summarize the news. Default is True.
        Returns:
            str: The latest news."""
        
        params = self.get_news_params(self.NEWS_API_KEY)
        params["sortBy"] = "publishedAt"
        news_information = "\n".join(self.get_articles(params))
        if summarize:
            news_information = self.llm.chat_completion(self.news_prompt, news_information)    
        if tts:
            self.tts.synthesize(f"Here are the latest news: {news_information}")
        return news_information
        
    @Skill.skill_feature
    def news_in_category(self, category: str="science", tts: bool=True, summarize: bool=True)->str:
        """Get the news in a category.
        Args:
            category (str): The category of the news. Default is "science".
            tts (bool): Whether to use text to speech. Default is True.
            summarize (bool): Whether to summarize the news. Default is True.
        Returns:
            str: The news in the category."""
        params = self.get_news_params(self.NEWS_API_KEY)
        params["category"] = category
        news_information = "\n".join(self.get_articles(params))
        if summarize:
            news_information = self.llm.chat_completion(self.news_prompt, news_information)
        if tts:
            self.tts.synthesize(f"Here are the latest news in {category}: {news_information}")
        return news_information
    
    @Skill.skill_feature
    def top_news(self, tts: bool=True) -> str:
        """Get the top news.
        Args:
            tts (bool): Whether to use text to speech. Default is True.
        Returns:
            str: The top news."""
        params = self.get_news_params(self.NEWS_API_KEY)
        news_information = "\n".join(self.get_articles(params))
        if tts:
            self.tts.synthesize(f"Heres the top news for today: {news_information}")
        return news_information

