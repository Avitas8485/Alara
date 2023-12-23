# this file contains all the routines for the hestia project
# for now, it will contain morning news routines
#  - so, 30 minutes before wake up time, hestia will prepare the news
#  - then, at wake up time, hestia will now read the news

from hestia.tools.news.newsapi import news_today, TODAYS_DATE
from hestia.tools.news.newsapi import(
    clean_news_summary, 
    extract_simplified_news, 
    generate_news_summary, 
    convert_news_summary_to_speech
    )

from hestia.text_to_speech.tts_utils import play_audio
from prefect import task, flow
from datetime import timedelta, datetime
# for now, lets assume that the user wants to wake up at 7:00 AM, and that the alarm is not needed
# so, we will set the wake up time to 7:00 AM


@task(name=f"Prepare News for {TODAYS_DATE}",
      description=f"This task will prepare the news for {TODAYS_DATE}, and will be run 30 minutes before wake up time",
      retries=3,
      retry_delay_seconds=60,
      tags=["news", "morning_routine"])
def prepare_news():
    news_today()
    clean_news_summary()
    extract_simplified_news()
    generate_news_summary()
    convert_news_summary_to_speech()
    
@task(name=f"Play News for {TODAYS_DATE}",
      description=f"This task will play the news for {TODAYS_DATE}, and will be run at wake up time",
      retries=3,
      retry_delay_seconds=60,
      tags=["news", "morning_routine"])
def play_news():
    news_summary_path = f"hestia/text_to_speech/outputs/news_summary/{TODAYS_DATE}summary.wav"
    play_audio(news_summary_path)
    





    


