from hestia.tools.reports.news_report import NewsReport
from hestia.tools.reports.weather_report import WeatherReport
from hestia.text_to_speech.tts_utils import play_audio
from datetime import datetime
import os
from hestia.tools.system_and_utility.scheduler import SchedulerManager
from hestia.lib.hestia_logger import logger
from hestia.tools.system_and_utility.alarm import Alarm




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
    news_report()
    weather_report()

    

def play_weather():
    logger.info("Playing weather report...")
    play_report("weather_report")
def play_news_details():
    logger.info("Playing news report...")
    play_report("news_report")
    

def morning_presentation():
    logger.info("Starting morning presentation...")
    alarm.start()
    play_weather()
    play_news_details()
    logger.info("Morning presentation complete. Cleaning up...")
    cleanup()
    
def cleanup():
    for file in os.listdir("hestia/text_to_speech/outputs"):
        if file.endswith(".wav"):
            os.remove(f"hestia/text_to_speech/outputs/{file}")
    for file in os.listdir("hestia/tools/reports/news"):
        if file.endswith(".txt"):
            os.remove(f"hestia/tools/reports/news/{file}")
    for file in os.listdir("hestia/tools/reports/weather"):
        if file.endswith(".txt"):
            os.remove(f"hestia/tools/reports/weather/{file}")
        
    

def schedule_morning_routine():
    scheduler.add_job(morning_preparation)
    scheduler.add_job(morning_presentation)
    
    
    