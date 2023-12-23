# this file contains all the routines for the hestia project
# for now, it will contain morning news routines
#  - so, 30 minutes before wake up time, hestia will prepare the news
#  - then, at wake up time, hestia will now read the news

from hestia.tools.reports.news_report import NewsReport
from hestia.tools.reports.weather_report import WeatherReport

from hestia.text_to_speech.tts_utils import play_audio
from prefect import task, flow
from datetime import timedelta, datetime
# for now, lets assume that the user wants to wake up at 7:00 AM, and that the alarm is not needed
# so, we will set the wake up time to 7:00 AM

news = NewsReport()
weather = WeatherReport()
TODAYS_DATE = datetime.now().strftime("%b %d, %Y")



@task(name="Fetch News",
        description="This task will fetch the news for today",
        retries=3,
        retry_delay_seconds=60,
        tags=["news", "morning_routine"])
def fetch_news():
    news_information = news.parse_information()
    
@task(name="Generate news summary",
      description="This task will generate the news summary for today",
      retries=3,
      retry_delay_seconds=60,
      tags=["news", "morning_routine"])
def generate_news_summary():
    news.generate_report_summary()
    
@task(name="Convert news summary to speech",
        description="This task will convert the news summary to speech",
        retries=3,
        retry_delay_seconds=60,
        tags=["news", "morning_routine"])
def convert_news_summary_to_speech():
    news.convert_summary_to_audio()
    
@task(name="Fetch Weather",
        description="This task will fetch the weather for today",
        retries=3,
        retry_delay_seconds=60,
        tags=["weather", "morning_routine"])
def fetch_weather():
    weather_information = weather.get_information()
    return weather_information

@task(name="Parse weather information",
        description="This task will parse the weather information",
        retries=3,
        retry_delay_seconds=60,
        tags=["weather", "morning_routine"])
def parse_weather_information(weather_information):
    weather_report = weather.parse_information(weather_information)
    return weather_report

@task(name="Generate weather summary",
        description="This task will generate the weather summary for today",
        retries=3,
        retry_delay_seconds=60,
        tags=["weather", "morning_routine"])
def generate_weather_summary():
    weather.generate_report_summary()
    
@task(name="Convert weather summary to speech",
        description="This task will convert the weather summary to speech",
        retries=3,
        retry_delay_seconds=60,
        tags=["weather", "morning_routine"])
def convert_weather_summary_to_speech():
    weather.convert_summary_to_audio()
    


@flow(name="News Report")
def news_report():
    fetch_news()
    generate_news_summary()
    convert_news_summary_to_speech()
    
@flow(name="Weather Report")
def weather_report():
    weather_information = fetch_weather()
    weather_report = parse_weather_information(weather_information)
    generate_weather_summary()
    convert_weather_summary_to_speech()
    
@flow(name="Morning Preparation")
def morning_preparation():
    news_report()
    weather_report()
    
    
    
@task(name="Play Weather for Today",
        description="This task will play the weather for today",
        retries=3,
        retry_delay_seconds=60,
        tags=["weather", "morning_routine"])
def play_weather():
    weather_report_path = f"hestia/text_to_speech/outputs/weather_report/{TODAYS_DATE}weather_report.wav"
    play_audio(weather_report_path)
    
@task(name="Play News details for Today",
        description="This task will play the news details for today",
        retries=3,
        retry_delay_seconds=60,
        tags=["news", "morning_routine"])
def play_news_details():
    news_details_path = f"hestia/text_to_speech/outputs/news_summary/{TODAYS_DATE}summary.wav"
    play_audio(news_details_path)
    
@flow(name="Morning Presentation")
def morning_presentation():
    play_weather()
    play_news_details()
    

if __name__ == "__main__":
    morning_preparation()
    morning_presentation()