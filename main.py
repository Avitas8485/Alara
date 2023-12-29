from flask import Flask, render_template, redirect, url_for
from hestia.tools.system_and_utility.scheduler import SchedulerManager
from hestia.lib.hestia_logger import logger
from flask_apscheduler import APScheduler
from datetime import datetime, timedelta
from hestia.routines.morning.morning_routine import schedule_morning_routine, morning_preparation, morning_presentation
app = Flask(__name__)

scheduler = SchedulerManager()
#schedule_morning_routine()
# lets add a job that executes immediately
"""scheduler.add_job(morning_preparation,trigger="date",run_date=datetime.now())
scheduler.add_job(morning_presentation,trigger="date",run_date=datetime.now() + timedelta(minutes=30))
scheduler.start_scheduler()"""
#morning_preparation()
morning_presentation()


@app.route("/")
def home():
    return render_template("index.html")







if __name__ == "__main__":
    app.run(debug=True)
    
    