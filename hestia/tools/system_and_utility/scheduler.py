from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from typing import Optional, Any, List
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from hestia.lib.hestia_logger import logger
from uuid import uuid4


JOBSTORES = {
    'default': SQLAlchemyJobStore(url='sqlite:///hestia/routines/jobs.sqlite')
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
    """Class to manage the scheduler.
    Attributes:
        scheduler: APscheduler instance"""
    def __init__(self):
        self.scheduler = BackgroundScheduler(jobstores=JOBSTORES, executors=EXECUTORS, job_defaults=JOB_DEFAULTS)

                
    def add_job(self, job_function: Any, job_id: Optional[str] = None, trigger: Optional[str] = None, **kwargs: Any) -> None:
        """Add a job to the scheduler.
        Args:
            job_function: The function to run.
            job_id: The id of the job.
            trigger: The trigger for the job.
            kwargs: The keyword arguments for the job."""
        # generate a job id if one is not provided
        if job_id is None:
            job_id = str(uuid4())
        # get all jobs from the scheduler
        if self.scheduler.get_job(job_id):
            logger.info(f"Job with id {job_id} already exists.")
            return 
        # add the job to the scheduler
        try:
            self.scheduler.add_job(job_function, trigger=trigger, id=job_id,replace_existing=True, **kwargs)
        except Exception as e:
            logger.error(f"Error adding job: {e}")

        
    def remove_job(self, job_id: str) -> None:
        """Remove a job from the scheduler.
        Args:
            job_id: The id of the job."""
        try:
            self.scheduler.remove_job(job_id)
        except Exception as e:
            logger.error(f"Error removing job: {e}")
        
    def get_jobs(self) -> List[Any]:
        """Get all jobs from the scheduler.
        Returns:
            List[Any]: The jobs."""
        try:
            return self.scheduler.get_jobs()
        except Exception as e:
            logger.error(f"Error getting jobs: {e}")
            return []        
    def modify_job(self, job_id: str, **changes: Any) -> None:
        """Modify a job.
        Args:
            job_id: The id of the job.
            changes: The changes to make to the job."""
        try:
            self.scheduler.modify_job(job_id, **changes)
        except Exception as e:
            logger.error(f"Error modifying job: {e}")
            return
        
    def pause_job(self, job_id: str) -> None:
        """Pause a job.
        Args:
            job_id: The id of the job."""
        try:
            self.scheduler.pause_job(job_id)
        except Exception as e:
            logger.error(f"Error pausing job: {e}")
            return
        
    def resume_job(self, job_id: str) -> None:
        """Resume a job.
        Args:
            job_id: The id of the job."""
        try:
            self.scheduler.resume_job(job_id)
        except Exception as e:
            logger.error(f"Error resuming job: {e}")
            return
        
    def stop_scheduler(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
        
    def start_scheduler(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
    



        


        

    
    