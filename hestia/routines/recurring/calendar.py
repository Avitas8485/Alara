from typing import Dict
from hestia.tools.notifications.notifications import notify
from hestia.skills.google_calendar import GoogleCalendar
from hestia.tools.scheduler import SchedulerManager
from datetime import datetime, timedelta
from hestia.lib.hestia_logger import logger


def get_events() -> list:
    calendar = GoogleCalendar()
    try:
        events = calendar.get_events_for_today()
    except Exception as e:
        logger.error(f"Failed to get events: {e}")
        events = []
    return events


def schedule_notification(scheduler: SchedulerManager, event: Dict):
    try:
        if "dateTime" in event["start"]:
            event_start = datetime.fromisoformat(event["start"]["dateTime"])
        else:
            event_start = datetime.fromisoformat(event["start"]["date"])
            event_start += timedelta(hours=9)
        notification_time = event_start - timedelta(minutes=60)
        scheduler.add_job(send_notification, trigger="date",
                          run_date=notification_time, args=[event])
    except Exception as e:
        logger.error(f"Failed to schedule notification: {e}")


def send_notification(event: Dict):
    title = event["summary"]
    message = (
        f"{event['summary']} at "
        f"{event['start'].get('dateTime', event['start'].get('date'))}"
        )
    try:
        notify(title, message)
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")


def main():
    events = get_events()
    scheduler = SchedulerManager()
    for event in events:
        schedule_notification(scheduler, event)


if __name__ == "__main__":
    main()
