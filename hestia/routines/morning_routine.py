from hestia.tools.reports.news_report import NewsReport
from hestia.tools.reports.weather_report import WeatherReport
from hestia.text_to_speech.tts_utils import play_audio
from datetime import datetime
import os
from hestia.lib.hestia_logger import HestiaLogger

logger = HestiaLogger().logger

WAKE_UP_TIME = datetime.now().replace(hour=7, minute=0, second=0, microsecond=0)
def generate_report(report_class):
    try:
        report = report_class()
        report.parse_information()
        report.generate_report_summary()
        report.convert_summary_to_audio()
    except Exception as e:
        logger.error(f"Error generating report: {e}")
    
def news_report():
    generate_report(NewsReport)
    
def weather_report():
    generate_report(WeatherReport)
    
def morning_preparation():
    news_report()
    weather_report()
    
def play_report(report_type):
    todays_date = datetime.now().strftime("%b %d, %Y")
    report_path = f"hestia/text_to_speech/outputs/{report_type}/{todays_date}{report_type}.wav"
    play_audio(report_path)
    
def play_weather():
    play_report("weather_report")
    
def play_news_details():
    play_report("news_report")
    
def morning_presentation():
    play_weather()
    play_news_details()
    
