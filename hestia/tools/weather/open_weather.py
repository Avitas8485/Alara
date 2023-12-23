     
# we are going to use visualcrossing.com for weather data

import requests
import sys
import os
from dotenv import load_dotenv
from typing import Optional
from hestia.llm.llama_chat_completion import chat_completion, load_weather_prompt
from hestia.text_to_speech.speech import TextToSpeechSystem


load_dotenv()
sys.path.insert(1,'C:/Users/avity/Projects/HESTIA/hestia')
from tools.system_and_utility.ip_geolocation import get_geolocation

API_KEY = os.getenv('VISUAL_CROSSING_API_KEY')
if not API_KEY:
    raise ValueError('Missing VISUAL_CROSSING_API_KEY environment variable')

BASE_URL = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/'

def get_city() -> str:
    """Returns city name"""
    location = get_geolocation()
    return location['city']

def get_weather_data(city: str) -> dict:
    """Returns weather data"""
    params = {
        'aggregateHours': '24',
        'combinationMethod': 'aggregate',
        'contentType': 'json',
        'includeAstronomy': 'true',
        'includeCurrent': 'true',
        'includeForecast': 'true',
        'locationMode': 'single',
        'key': API_KEY,
        'location': city
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"Error fetching weather data: {e}")
        return None
    
def get_weather_report() -> Optional[str]:
    """Returns weather report"""
    city = get_city()
    weather_data = get_weather_data(city)
    if not weather_data:
        return None
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
        'Conditions Description': weather_data['days'][0]['icon']
        }
    for key, value in report_items.items():
        weather_report += f"{key}: {value}\n"
    return weather_report

def generate_weather_report() -> Optional[str]:
    """Generates weather report"""
    weather_report = get_weather_report()
    if not weather_report:
        return None
    return chat_completion(sytem_prompt=load_weather_prompt(), user_prompt=weather_report)["choices"][0]["message"]["content"]


    
    
    
    
if __name__ == '__main__':
    report = get_weather_report()
    if report:
        print(report)
    else:
        print("Error fetching weather data")