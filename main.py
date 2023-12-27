from hestia.routines.morning.morning_routine import schedule_morning_routine
from hestia.lib.hestia_logger import HestiaLogger

logger = HestiaLogger().logger




if __name__ == "__main__":
    logger.info("Starting morning routine...")
    schedule_morning_routine()
    