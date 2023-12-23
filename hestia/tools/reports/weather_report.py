from hestia.tools.reports.base_report_generator import BaseReportGenerator
import requests
import sys
import os
from dotenv import load_dotenv
from hestia.llm.llama_chat_completion import chat_completion, load_weather_prompt
from hestia.text_to_speech.speech import TextToSpeechSystem
from datetime import datetime

load_dotenv()
sys.path.insert(1,'C:/Users/avity/Projects/HESTIA/hestia')

from tools.system_and_utility.ip_geolocation import get_geolocation


class WeatherReport(BaseReportGenerator):
    WEATHER_API_KEY = os.getenv('VISUAL_CROSSING_API_KEY')
    BASE_URL = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/'

    def __init__(self):
        self.todays_date = datetime.now().strftime("%b %d, %Y")
        self.DIR_PATH = "hestia/tools/reports/weather"
        self.simplified_weather_path = os.path.join(self.DIR_PATH, f"{self.todays_date}simplified.txt")
        self.weather_report_path = os.path.join(self.DIR_PATH, f"weather_report {self.todays_date}.txt")

    def write_file(self, file_path, content):
        with open(file_path, "w") as f:
            f.write(content)

    def read_file(self, file_path):
        with open(file_path, "r") as f:
            return f.read()

    def get_city(self) -> str:
        """Returns city name"""
        location = get_geolocation()
        return location['city']

    def get_information(self)-> dict:
        """Returns weather data"""
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
            print(f"Error fetching weather data: {e}")
            return {}

    def parse_information(self):
        """Returns weather report"""
        weather_data = self.get_information()
        if not weather_data:
            return None
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
        self.write_file(self.simplified_weather_path, weather_report)
        
    def generate_report_summary(self):
        weather = self.read_file(self.simplified_weather_path)
        weather_prompt = load_weather_prompt()[0]
        weather_report = chat_completion(sytem_prompt=weather_prompt, user_prompt=weather)
        self.write_file(self.weather_report_path, weather_report)

    def convert_summary_to_audio(self):
        weather = self.read_file(self.weather_report_path)
        tts = TextToSpeechSystem()
        if weather is None:
            return
        tts.convert_text_to_speech_using_nlp(
            text=weather,
            output_dir="hestia/text_to_speech/outputs/weather_report",
            output_filename=f"{self.todays_date}weather_report"
        )