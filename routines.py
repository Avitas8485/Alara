
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler
from hestia.routines.morning_routine import morning_preparation, morning_presentation
import logging
# for now, lets assume that the user wants to wake up at 7:00 AM, and that the alarm is not needed
# so, we will set the wake up time to 7:00 AM


logging.basicConfig(filename='scheduler.log', level=logging.INFO)

    
jobstore = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}

executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}

job_defaults = {
    'coalesce': False,
    'max_instances': 3,
    'misfire_grace_time': 500
}

scheduler = BlockingScheduler(jobstores=jobstore, executors=executors, job_defaults=job_defaults)

def remove_job(job_id):
    try:
        scheduler.remove_job(job_id)
    except Exception as e:
        print(f"Error removing job: {e}")
try:
    scheduler.add_job(morning_preparation, 'cron' , hour=6, minute=30, id="morning_preparation")
    scheduler.add_job(morning_presentation, 'cron' , hour=7, minute=0, id="morning_presentation")
    scheduler.add_job(remove_job, 'cron' , hour=7, minute=5, args=["morning_preparation"])
    scheduler.add_job(remove_job, 'cron' , hour=7, minute=5, args=["morning_presentation"])
except Exception as e:
    logging.error(f"Error adding job: {e}")
    
if __name__ == "__main__":
    scheduler.start()

    



