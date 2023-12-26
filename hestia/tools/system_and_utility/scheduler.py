from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from typing import Optional, Any

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from hestia.lib.hestia_logger import HestiaLogger

logger = HestiaLogger().logger

JOBSTORES = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}

EXECUTORS = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}

JOB_DEFAULTS = {
    'coalesce': False,
    'max_instances': 3,
    'misfire_grace_time': 500
}

scheduler = BackgroundScheduler(jobstores=JOBSTORES, executors=EXECUTORS, job_defaults=JOB_DEFAULTS)

def add_job(job_function, job_id, trigger, args):
    try:
        existing_jobs = [job.id for job in scheduler.get_jobs()]
        if job_id in existing_jobs:
            scheduler.remove_job(job_id)
        scheduler.add_job(job_function, trigger=trigger, id=job_id, args=args)
    except Exception as e:
        logger.error(f"Error adding job: {e}")
        raise

def remove_job(job_id):
    try:
        scheduler.remove_job(job_id)
    except Exception as e:
        logger.error(f"Error removing job: {e}")
        raise

def start_scheduler():
    if not scheduler.running:
        scheduler.start()

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        
def pause_job(job_id):
    try:
        scheduler.pause_job(job_id)
    except Exception as e:
        logger.error(f"Error pausing job: {e}")
        raise
    
def resume_job(job_id):
    try:
        scheduler.resume_job(job_id)
    except Exception as e:
        logger.error(f"Error resuming job: {e}")
        raise
    
def list_jobs():
    try:
        jobs = scheduler.get_jobs()
        for job in jobs:
            print(f"Job: {job.id} - {job.next_run_time}")
        return jobs
    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        raise
    
def modify_job(job_id, job_function=None, trigger=None, args=None):
    try:
        if job_function:
            scheduler.modify_job(job_id, job_function=job_function)
        if trigger:
            scheduler.modify_job(job_id, trigger=trigger)
        if args:
            scheduler.modify_job(job_id, args=args)
    except Exception as e:
        logger.error(f"Error modifying job: {e}")
        raise