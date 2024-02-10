from flask import Flask, render_template
from hestia.tools.system_and_utility.scheduler import SchedulerManager
from hestia.lib.hestia_logger import logger
from hestia.routines.morning.morning_routine import morning_preparation, play_morning_greeting, morning_greeting
from hestia.routines.recurring.calendar import get_events, send_notification
from datetime import datetime, timedelta

import os
app = Flask(__name__)
'''
scheduler = SchedulerManager()
scheduler.start_scheduler()
def schedule_morning_routine():
    """Schedule the morning routine."""
    logger.info("Scheduling morning routine...")
    scheduler.add_job(morning_preparation,trigger="cron",hour=7,minute=00)
    scheduler.add_job(morning_presentation,trigger="cron",hour=7,minute=40)
    logger.info("Morning routine scheduled.")

def schedule_calendar_notification():
    try:
        events = get_events()
        for event in events:
            if "dateTime" in event["start"]:
                event_start = datetime.fromisoformat(event["start"]["dateTime"])
            else:
                event_start = datetime.fromisoformat(event["start"]["date"]) + timedelta(hours=9)
            notification_time = event_start - timedelta(minutes=60)
            scheduler.add_job(send_notification, trigger="date", run_date=notification_time, args=[event])
            logger.info(f"Notification for {event['summary']} scheduled at {notification_time}")
    except Exception as e:
        logger.error(f"Failed to schedule notification: {e}")

schedule_morning_routine()
schedule_calendar_notification()'''

morning_preparation()

play_morning_greeting()



@app.route("/")
def home():
    return render_template("index.html")







if __name__ == "__main__":
    app.run(debug=False)
    
    