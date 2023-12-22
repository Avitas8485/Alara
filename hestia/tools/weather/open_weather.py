import datetime as dt
import requests
import sys
import os
from dotenv import load_dotenv
from typing import Optional


load_dotenv()
sys.path.append('/home/avity/Automation')
from system_and_utility.ip_geolocation import get_geolocation

API_KEY = os.getenv('OPEN_WEATHER_API_KEY')
if not API_KEY:
    raise ValueError('Missing OPEN_WEATHER_API_KEY environment variable')
BASE_URL = 'https://api.openweathermap.org/data/2.5/weather?'


def get_city() -> str:
    """Returns city name"""
    location = get_geolocation()
    return location['city']



def get_weather_data(city: str) -> dict:
    """Returns weather data"""
    params = {
        'q': city,
        'appid': API_KEY
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"Error fetching weather data: {e}")
        return None

def kelvin_to_celsius(kelvin_temp: float) -> float:
    """Converts kelvin to celsius"""
    return round((kelvin_temp - 273.15), 2)

def celsius_to_fahrenheit(celsius_temp: float) -> float:
    """Converts celsius to fahrenheit"""
    # two decimal places
    return round((celsius_temp * 9/5) + 32, 2)

def get_weather_report() -> Optional[str]:
    """Returns weather report"""
    city = get_city()
    weather_data = get_weather_data(city)
    if not weather_data:
        return None
    weather_report = f"""Weather report for {city}:\n"""
    report_items = {
        'Temperature': kelvin_to_celsius(weather_data['main']['temp']),
        'Feels like': kelvin_to_celsius(weather_data['main']['feels_like']),
        'Weather description': weather_data['weather'][0]['description'],
        'Wind speed': weather_data['wind']['speed'],
        'Sunrise time': dt.datetime.fromtimestamp(weather_data['sys']['sunrise']).strftime('%H:%M:%S'),
        'Sunset time': dt.datetime.fromtimestamp(weather_data['sys']['sunset']).strftime('%H:%M:%S'),
        'Humidity': weather_data['main']['humidity'],
        'Pressure': weather_data['main']['pressure'],
        'Visibility': weather_data['visibility']
    }
    for key, value in report_items.items():
        weather_report += f"{key}: {value}\n"
    return weather_report


if __name__ == '__main__':
    report = get_weather_report()
    if report:
        print(report)
    else:
        print("Error fetching weather data")