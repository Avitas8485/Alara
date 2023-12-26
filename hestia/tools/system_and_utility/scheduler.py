from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from typing import Optional, Any, List
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

class SchedulerManager:
    def __init__(self):
        self.scheduler = BackgroundScheduler(jobstores=JOBSTORES, executors=EXECUTORS, job_defaults=JOB_DEFAULTS)

                
    def add_job(self, job_function: Any, job_id: str, trigger, args: List[Any]):
        try:
            self.scheduler.remove_job(job_id)
        except Exception:
            pass
        try:
            self.scheduler.add_job(job_function, trigger=trigger, id=job_id, args=args)
        except Exception as e:
            logger.error(f"Error adding job: {e}")
            raise
        
    def remove_job(self, job_id: str):
        try:
            self.scheduler.remove_job(job_id)
        except Exception as e:
            logger.error(f"Error removing job: {e}")
            raise
        
    def pause_job(self, job_id: str):
        try:
            self.scheduler.pause_job(job_id)
        except Exception as e:
            logger.error(f"Error pausing job: {e}")
            raise
        
    def resume_job(self, job_id: str):
        try:
            self.scheduler.resume_job(job_id)
        except Exception as e:
            logger.error(f"Error resuming job: {e}")
            raise
        
    def list_jobs(self) -> str:
        try:
            jobs = self.scheduler.get_jobs()
            return "\n".join([f"{job.id} {job.next_run_time}" for job in jobs]) if jobs else "No jobs"
        except Exception as e:
            logger.error(f"Error listing jobs: {e}")
            raise
        
    def modify_job(self, job_id: str, job_function: Optional[Any] = None, trigger=None, args=None):
        try:
            modifications = {key: value for key, value in [('job_function', job_function), ('trigger', trigger), ('args', args)] if value is not None}
            self.scheduler.modify_job(job_id, **modifications)
        except Exception as e:
            logger.error(f"Error modifying job: {e}")
            raise
        
    def stop_scheduler(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
        
    def start_scheduler(self):
        if not self.scheduler.running:
            self.scheduler.start()
    
    def __del__(self):
        self.stop_scheduler()
        

    
    