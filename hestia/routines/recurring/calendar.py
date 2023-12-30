from HESTIA.hestia.tools.system_and_utility.notifications.notifications import notify
from HESTIA.hestia.tools.system_and_utility.google_calendar import GoogleCalendar
from HESTIA.hestia.tools.system_and_utility.scheduler import SchedulerManager
from datetime import datetime, timedelta



calendar = GoogleCalendar()
events = calendar.get_events_list()

scheduler = SchedulerManager()

def send_notification(event):
    title = event["summary"]
    message = f"{event['summary']} at {event['start'].get('dateTime', event['start'].get('date'))}"
    notify(title, message)
    
for event in events:
    event_start = datetime.fromisoformat(event["start"].get("dateTime", event["start"].get("date")))
    notification_time = event_start - timedelta(minutes=60)
    scheduler.add_job(send_notification, trigger="date", run_date=notification_time, args=[event])