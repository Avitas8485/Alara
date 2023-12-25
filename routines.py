from hestia.lib.hestia_logger import HestiaLogger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler
from hestia.routines.morning_routine import morning_preparation, morning_presentation
from decouple import config

# Set up logging
logger = HestiaLogger().logger

# Get settings from environment variables
db_url = config('DB_URL', default='sqlite:///jobs.sqlite')
thread_pool_size = config('THREAD_POOL_SIZE', default=20, cast=int)
process_pool_size = config('PROCESS_POOL_SIZE', default=5, cast=int)

# Set up job store, executors and job defaults
jobstore = {'default': SQLAlchemyJobStore(url=db_url)}
executors = {
    'default': ThreadPoolExecutor(thread_pool_size),
    'processpool': ProcessPoolExecutor(process_pool_size)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3,
    'misfire_grace_time': 500
}

# Create scheduler
scheduler = BlockingScheduler(jobstores=jobstore, executors=executors, job_defaults=job_defaults)

def remove_job(job_id):
    try:
        scheduler.remove_job(job_id)
    except Exception as e:
        logger.error(f"Error removing job: {e}")

def schedule_jobs():
    try:
        scheduler.add_job(morning_preparation, 'cron' , hour=6, minute=30, id="morning_preparation")
        scheduler.add_job(morning_presentation, 'cron' , hour=7, minute=0, id="morning_presentation")
        scheduler.add_job(remove_job, 'cron' , hour=7, minute=5, args=["morning_preparation"])
        scheduler.add_job(remove_job, 'cron' , hour=7, minute=5, args=["morning_presentation"])
    except Exception as e:
        logger.error(f"Error scheduling jobs: {e}")

if __name__ == "__main__":
    schedule_jobs()
    scheduler.start()