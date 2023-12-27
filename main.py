from hestia.routines.morning.morning_routine import schedule_morning_routine
from hestia.tools.system_and_utility.scheduler import SchedulerManager
from hestia.lib.hestia_logger import logger





if __name__ == "__main__":
    scheduler = SchedulerManager()
    while True:
        try:
            schedule_morning_routine()
            logger.info("Hestia is now running. Press Ctrl+C to stop.")
            scheduler.start_scheduler()
        except KeyboardInterrupt:
            logger.info("Stopping Hestia...")
            scheduler.stop_scheduler()
            break
            
