import requests
from dotenv import load_dotenv
from hestia.tools.ip_geolocation import get_geolocation
from hestia.config.config import cfg
from hestia.skills.base_skill import Skill
from hestia.llm.llama_chat_completion import LlamaChatCompletion, load_prompt_txt
from hestia.tts.piper_tts import PiperTTS
load_dotenv()

class Weather(Skill):
    """A class to represent a WeatherReport.
    Attributes:
        WEATHER_API_KEY: The API key for the Visual Crossing Weather API.
        BASE_URL: The base URL for the Visual Crossing Weather API."""
    WEATHER_API_KEY = cfg.VISUAL_CROSSING_API_KEY
    BASE_URL = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/'
    
    def __init__(self):
        """Initialize the Weather skill.
        Attributes:
            DIR_PATH: The path to the directory where the weather report is stored.
            simplified_weather_path: The path to the simplified weather.
            weather_report_path: The path to the weather report."""
            
        
        self.llm = LlamaChatCompletion()
        self.weather_prompt = load_prompt_txt("weather_report")
        self.tts = PiperTTS()
        self.city = self.get_city()
        
    def get_city(self) -> str:
        """Returns city name"""
        location = get_geolocation()
        return location['city']
    
    def fetch_weather(self, city=None) -> dict:
        """Fetch weather data
        Args:
            city: The city to fetch the weather data for.
            Returns:
                dict: The weather data."""
        if city is None:
            city = self.city
        params = {
            'aggregateHours': '24',
            'combinationMethod': 'aggregate',
            'contentType': 'json',
            'includeAstronomy': 'true',
            'includeCurrent': 'true',
            'includeForecast': 'true',
            'locationMode': 'single',
            'key': self.WEATHER_API_KEY,
            'unitGroup': 'us',
            'location': city
        }
        response = requests.get(self.BASE_URL, params=params)
        return response.json()
    
    def current_weather(self, city=None, tts=True) -> str:
        """Get the current weather.
        Args:
            city: The city to get the current weather for.
            Returns:
                str: The current weather."""
        if not city:
            city = self.city
        weather_data = self.fetch_weather(city)
        if not weather_data:
            return 'None'
        weather_report = f"""Weather report for {city}:\n"""
        report_items = {
            'Address': weather_data['address'],
        'Description': weather_data['description'],
        'Day': weather_data['days'][0]['datetime'],
        'Max Temperature': weather_data['days'][0]['tempmax'],
        'Min Temperature': weather_data['days'][0]['tempmin'],
        'Current Temperature': weather_data['currentConditions']['temp'],
        'Humidity': weather_data['days'][0]['humidity'],
        'Pressure': weather_data['days'][0]['pressure'],
        'Wind Speed': weather_data['days'][0]['windspeed'],
        'Wind Gust': weather_data['days'][0]['windgust'],
        'Sunrise Time': weather_data['days'][0]['sunrise'],
        'Sunset Time': weather_data['days'][0]['sunset'],
        'Conditions': weather_data['days'][0]['conditions'],
        'Conditions Description': weather_data['days'][0]['icon'],
        }
        for key, value in report_items.items():
            weather_report += f"{key}: {value}\n"
        summary = self.llm.chat_completion(self.weather_prompt, weather_report)
        if tts:
            self.tts.synthesize(summary)
        return summary
        
    
    
        
    
    
    
    