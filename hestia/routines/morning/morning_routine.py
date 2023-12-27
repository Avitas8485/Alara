from hestia.tools.reports.news_report import NewsReport
from hestia.tools.reports.weather_report import WeatherReport
from hestia.text_to_speech.tts_utils import play_audio
from datetime import datetime
import os
from hestia.tools.system_and_utility.scheduler import SchedulerManager
from hestia.lib.hestia_logger import HestiaLogger
from hestia.tools.system_and_utility.alarm import Alarm



logger = HestiaLogger().logger
alarm = Alarm()
scheduler = SchedulerManager()

def generate_report(report_class):
    try:
        report = report_class()
        report.parse_information()
        report.generate_report_summary()
        report.convert_summary_to_audio()
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        
def play_report(report_type):
    todays_date = datetime.now().strftime("%b %d, %Y")
    report_path = f"hestia/text_to_speech/outputs/{report_type}/{todays_date}{report_type}.wav"
    play_audio(report_path)

def news_report():
    generate_report(NewsReport)
    
def weather_report():
    generate_report(WeatherReport)

def morning_preparation():
    alarm.start()
    news_report()
    weather_report()

    

def play_weather():
    play_report("weather_report")
def play_news_details():
    play_report("news_report")
    

def morning_presentation():
    play_weather()
    play_news_details()
    
def cleanup():
    for file in os.listdir("hestia/text_to_speech/outputs"):
        os.remove(f"hestia/text_to_speech/outputs/{file}")
    for file in os.listdir("hestia/tools/reports/news"):
        os.remove(f"hestia/tools/reports/news/{file}")
    for file in os.listdir("hestia/tools/reports/weather"):
        os.remove(f"hestia/tools/reports/weather/{file}")
        
    

def schedule_morning_preparation():
    scheduler.add_job(morning_preparation, trigger="cron", hour=6, minute=0, second=0)
    scheduler.add_job(morning_presentation, trigger="cron", hour=7, minute=0, second=0)
    