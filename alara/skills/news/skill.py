import os
import requests
from dotenv import load_dotenv
from newspaper import Article
from newspaper import Config
from datetime import datetime
import nltk
from typing import List
from alara.skills.skill_manager import Skill
from alara.tts.piper_tts import PiperTTS
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
        self.tts = PiperTTS()
        self.llm = LlmEngine.load_llm()
        self.news_prompt = load_prompt("news_debrief")
        
    
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
            #logger.error(f"Error making news request: {e}")
            raise
        
    def parse_news_response(self, response: requests.Response):
        """Parse the news response.
        Args:
            response (requests.Response): The response from the news request.
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
    
    
    def download_and_parse_article(self, article_info: dict, config: Config)->Article:
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
            article_info (dict): The information about the article.
            article (Article): The article.
        Returns:
            dict: The article information."""
        self.todays_date = datetime.now().strftime("%b %d, %Y")
        article.nlp()
        summary = self.encode_to_ascii(article.summary.replace("\n", ""))
        title = self.encode_to_ascii(article_info["title"])
        return {"title": title, "summary": summary, "url": article_info["url"], "date": f"{self.todays_date}"}
    
    def get_articles(self, params: dict)->dict:
        """Get the articles.
        Args:
            params (dict): The parameters for the news request.
        Returns:
            dict: The articles."""
        articles_dict = dict()
        response = self.make_news_request(params)
        news_articles = self.parse_news_response(response)
        for articles in news_articles:
            try:
                article = self.download_and_parse_article(articles, self.get_config())
            except Exception as e:
                logger.error(f"Error downloading article: {e}")
                continue
            articles = self.get_article_info(articles, article)
            articles_dict[articles["title"]] = articles
        return articles_dict
    
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
        latest_news = self.get_articles(params)
        news_information = "\n".join([value["title"] + "." for value in latest_news.values()])
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
        news_in_category = self.get_articles(params)
        news_information = "\n".join([value["title"] + "." for value in news_in_category.values()])
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
        top_news = self.get_articles(params)
        news_information = "\n".join([value["title"] + "." for value in top_news.values()])
        if tts:
            self.tts.synthesize(f"Heres the top news for today: {news_information}")
        return news_information
    
    
    
        


    def parse_information(self, news: dict)->str:
        """Parse the news information.
        Args:
            news (dict): The news information.
        Returns:
            str: The parsed news information."""
        
        news = {k: v for k, v in news.items() if k != "[Removed]"}
        for key, value in news.items():
            value.pop("url", None)
            value.pop("date", None)
            value["title"] = self.encode_to_ascii(value.get("title", ""))
            value["summary"] = self.encode_to_ascii(value.get("summary", ""))
        news_information = [value["title"] + "." for value in news.values()]
        return "\n".join(news_information)

