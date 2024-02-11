from hestia.tools.reports.base_report_generator import BaseReportGenerator
import requests
import os
from dotenv import load_dotenv
from hestia.llm.llama_chat_completion import chat_completion, load_prompt, load_prompt_txt
from hestia.text_to_speech.speech import TextToSpeechSystem
from hestia.tools.system_and_utility.ip_geolocation import get_geolocation
from hestia.lib.hestia_logger import logger
from datetime import datetime
from hestia.config.config import cfg
load_dotenv()


class WeatherReport(BaseReportGenerator):
    """A class to represent a WeatherReport.
    Attributes:
        WEATHER_API_KEY: The API key for the Visual Crossing Weather API.
        BASE_URL: The base URL for the Visual Crossing Weather API."""
    WEATHER_API_KEY = cfg.VISUAL_CROSSING_API_KEY
    BASE_URL = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/'

    def __init__(self):
        """Initialize the WeatherReport.
        Attributes:
            todays_date: The date of the weather report.
            DIR_PATH: The path to the directory where the weather report is stored.
            simplified_weather_path: The path to the simplified weather.
            weather_report_path: The path to the weather report."""
            
        self.todays_date = datetime.now().strftime("%b %d, %Y")
        self.weather_summary_path = os.path.join(cfg.REPORT_SUMMARY_PATH, f"weather_summary {self.todays_date}.txt")
    def write_file(self, file_path: str, content):
        """Write to a file.
        Args:
            file_path: The path to the file.
            content: The content to write to the file."""
        with open(file_path, "w") as f:
            f.write(content)

    def read_file(self, file_path: str)->str:
        """Read a file.
        Args:
            file_path: The path to the file.
        Returns:
            str: The content of the file."""
        with open(file_path, "r") as f:
            return f.read()

    def get_city(self) -> str:
        """Returns city name"""
        location = get_geolocation()
        return location['city']

    def get_information(self)-> dict:
        """Returns weather data
        Returns:
            dict: The weather data."""
        params = {
            'aggregateHours': '24',
            'combinationMethod': 'aggregate',
            'contentType': 'json',
            'includeAstronomy': 'true',
            'includeCurrent': 'true',
            'includeForecast': 'true',
            'locationMode': 'single',
            'key': self.WEATHER_API_KEY,
            'location': self.get_city()
        }
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error making weather request: {e}")
            return {}

    def parse_information(self)-> str:
        """Returns weather report"""
        weather_data = self.get_information()
        if not weather_data:
            return 'None'
        weather_report = f"""Weather report for {self.get_city()}:\n"""
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
        return weather_report
        
    def generate_report_summary(self):
        """Generate the weather report summary."""
        weather =  self.parse_information()

        weather_prompt = load_prompt_txt(prompt_name="weather_report")
        weather_report = chat_completion(system_prompt=weather_prompt, user_prompt=weather)
        self.write_file(self.weather_summary_path, weather_report)

    def convert_summary_to_audio(self):
        """Convert the weather report summary to audio using text to speech."""
        weather = self.read_file(self.weather_summary_path)
        tts = TextToSpeechSystem()
        if weather is None:
            return
        tts.convert_text_to_speech(
            text=weather,
            output_dir="hestia/text_to_speech/outputs/weather_report",
            output_filename=f"{self.todays_date}weather_report"
        )
        
    def generate_report(self):
        """Generate the weather report."""
        self.generate_report_summary()
        self.convert_summary_to_audio()