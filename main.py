from flask import Flask, render_template
from hestia.tools.system_and_utility.scheduler import SchedulerManager
from hestia.lib.hestia_logger import logger
from hestia.routines.morning.morning_routine import morning_preparation, morning_presentation

import os
app = Flask(__name__)

scheduler = SchedulerManager()
scheduler.start_scheduler()
def schedule_morning_routine():
    """Schedule the morning routine."""
    logger.info("Scheduling morning routine...")
    scheduler.add_job(morning_preparation,trigger="cron",hour=00,minute=7)
    scheduler.add_job(morning_presentation,trigger="cron",hour=00,minute=42)
    logger.info("Morning routine scheduled.")


schedule_morning_routine()



@app.route("/")
def home():
    return render_template("index.html")







if __name__ == "__main__":
    app.run(debug=False)
    
    