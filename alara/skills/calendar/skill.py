import requests
from icalendar import Calendar as Icalendar
from icalendar import Event, vDatetime, vRecur
from datetime import datetime, date, timedelta
from dateutil.rrule import rrulestr
from dateutil.parser import parse
from dateutil.tz import gettz, tzlocal
from typing import List, Dict, Optional, Any
import pytz
import os
from alara.lib.singleton import Singleton
from alara.lib.logger import logger
from alara.tools.notifications.notifications import NotificationTool, NotificationType
from alara.tools.scheduler import SchedulerManager
from alara.tts.tts_engine import TTSEngine
from alara.skills.skill_manager import Skill

class CalendarEvent:
    """A class to represent a calendar event.
    Attributes:
        summary (str): The summary of the event. Required but defaults to "Untitled Event".
        dtstart (datetime): The start date and time of the event. Required but defaults None.
        dtend (datetime): The end date and time of the event. Required but defaults None.
        rrule (str): The recurrence rule of the event. Optional.
        location (str): The location of the event. Optional.
        description (str): The description of the event. Optional."""
    def __init__(self,
                 summary: str="Untitled Event",
                dtstart: Optional[datetime] = None,
                dtend: Optional[datetime] = None,
                rrule: Optional[str] = None,
                location: Optional[str] = None,
                description: Optional[str] = None):
        self.summary = summary
        self.dtstart = dtstart if dtstart is not None else datetime.now()
        self.dtend = dtend if dtend is not None else (self.dtstart + timedelta(minutes=30) if self.dtstart else (datetime.now() + timedelta(minutes=30)))
        self.rrule = rrule
        self.location = location
        self.description = description
     
    def _validate_event(self)->bool:
        required_fields = ["summary", "dtstart", "dtend"]
        for field in required_fields:
            if not getattr(self, field):
                print(f"Error: {field} is required")
                return False
        return True
        
    def to_dict(self)->Dict[str, Any]:
        return {
            "summary": self.summary,
            "dtstart": self.dtstart.strftime("%Y-%m-%d %H:%M:%S"),
            "dtend": self.dtend.strftime("%Y-%m-%d %H:%M:%S"),
            "rrule": self.rrule,
            "location": self.location,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            summary=data["summary"],
            dtstart=parse(data["dtstart"]),
            dtend=parse(data["dtend"]),
            rrule=data.get("rrule"),
            location=data.get("location"),
            description=data.get("description")
        )
        
    
    def to_event(self)->Event:
        event = Event()
        event.add("summary", self.summary)
        event.add("dtstart", vDatetime(self.dtstart))
        event.add("dtend", vDatetime(self.dtend))
        if self.rrule:
            event.add("rrule", vRecur.from_ical(self.rrule))
        if self.location:
            event.add("location", self.location)
        if self.description:
            event.add("description", self.description)
        return event
        
    def __str__(self):
        return f"Summary: {self.summary}, Start: {self.dtstart}, End: {self.dtend}, RRULE: {self.rrule}, Location: {self.location}, Description: {self.description}"
    
@Skill.eager_load     
class Calendar(Skill, metaclass=Singleton):
    def __init__(self):
        self.tts_engine = TTSEngine.load_tts()
        self.calendars = Icalendar()
        self.notification_tool = NotificationTool()
        self.scheduler_manager = SchedulerManager()
        self.refresh_interval = 60
        self.calendar_links = []
        self.runtime_events = []
        self.load_links_from_file()
        self.scheduler_manager.add_job(
            job_function=self.refresh_calendars,
            trigger="interval",
            seconds=self.refresh_interval
        )
        
           
    def load_links_from_file(self, file_path: str='alara/skills/calendar/ics_links.txt'):
        """Load calendar links from a file.
        Args:
            file_path (str): The path to the file containing calendar links."""
        if not os.path.exists(file_path):
            logger.error(f"Error: {file_path} does not exist")
            return
        with open(file_path, "r") as file:
            for line in file:
                self.calendar_links.append(line.strip())
                self.load_ics_calendar(line.strip())
        
                
    def refresh_calendars(self):
        """Refresh the calendars by loading the calendar links from the file."""
        for link in self.calendar_links:
            self.load_ics_calendar(link)
        self.update_scheduled_events()
        for event in self.runtime_events:
            self.schedule_event(event)
        
        
        
            
    def update_scheduled_events(self):
        """Update the scheduled events based on the current calendar data."""
        # Remove all previously scheduled events
        scheduled_events = self.scheduler_manager.get_jobs()
        for event in scheduled_events:
            event_id = event.id
            if event_id.startswith("CAL_") or event_id.startswith("CAL_TTS_NOTIFICATION_"):
                try:
                    logger.info(f"Removing job: {event_id}")
                    if self.scheduler_manager.get_job(event_id):
                        self.scheduler_manager.remove_job(job_id=event_id)
                except Exception as e:
                    logger.error(f"Error: {e}")
                    pass
    
        # reschedule today's events
        today_events = self.get_today_events()
        for event in today_events:
            self.schedule_event(CalendarEvent.from_dict(event))
        
    
    def load_ics_calendar(self, url: str):
        """Load an ics calendar from a URL.
        Args:
            url (str): The URL of the calendar.
            Returns:
                None."""
        logger.info(f"Loading calendar from {url}")
        try:
            response = requests.get(url)
            response.raise_for_status()
            calendar = Icalendar.from_ical(response.text)
            for component in calendar.walk("VEVENT"):
                self.calendars.add_component(component)
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")
        try:
            today_events = self.get_today_events()
            for event in today_events:
                # schedule only future events
                dtstart = parse(event["dtstart"]).replace(tzinfo=tzlocal())
                if dtstart > datetime.now(tzlocal()):
                    self.schedule_event(CalendarEvent.from_dict(event))
                
                
        except Exception as e:
            logger.error(f"Error: {e}")
    
    
    def add_event(self, event: CalendarEvent):
        """Add an event to the calendar.
        Args:
            event (CalendarEvent): The event to add to the calendar.
            Returns:
                None."""
        if not event._validate_event():
            return
        self.calendars.add_component(event.to_event())   
        logger.info(f"Event added: {event}")
        self.schedule_event(event) 
        self.runtime_events.append(event)        
    
    def fetch_event(self, summary: str):
        """Fetch an event from the calendar.
        Args:
            summary (str): The summary of the event to fetch.
        """
        for component in self.calendars.walk("VEVENT"):
            if component.get("summary") == summary:
                return component
        return None
    
    def update_event(self, event: CalendarEvent):
        """Update an event in the calendar.
        Args:
            event (CalendarEvent): The event to update in the calendar.
            """
        component = self.fetch_event(event.summary)  
        if component:
            del component["summary"]
            component.add("summary", event.summary)
            del component["dtstart"]
            component.add("dtstart", vDatetime(event.dtstart))
            del component["dtend"]
            component.add("dtend", vDatetime(event.dtend))
            if event.rrule:
                del component["rrule"]
                component.add("rrule", vRecur.from_ical(event.rrule))
            if event.location:
                del component["location"]
                component.add("location", event.location)
            if event.description:
                del component["description"]
                component.add("description", event.description)
            self.scheduler_manager.remove_job(job_id=f"CAL_{event.summary} @ {event.dtstart}")
            self.scheduler_manager.remove_job(job_id=f"CAL_TTS_NOTIFICATION_{event.summary} @ {event.dtstart}")
            self.schedule_event(event)
            logger.info(f"Event updated: {event}")
    
    def delete_event(self, event: CalendarEvent):
        """Delete an event from the calendar.
        Args:
            event (CalendarEvent): The event to delete from the calendar.
            """
        component = self.fetch_event(event.summary)
        if component:
            self.calendars.subcomponents.remove(component)
            logger.info(f"Event deleted: {event}")
            self.scheduler_manager.remove_job(job_id=f"CAL_{event.summary} @ {event.dtstart}")
            self.scheduler_manager.remove_job(job_id=f"CAL_TTS_NOTIFICATION_{event.summary} @ {event.dtstart}")
        
            
    def notify_event(self, event: CalendarEvent):
        self.notification_tool._run(
            title=event.summary, 
            message=f"Event: {event.summary} is scheduled for {event.dtstart.strftime('%Y-%m-%d %H:%M')}",
            notification_type=NotificationType.REMINDER
        )
        
        
    from dateutil.tz import gettz

    def schedule_event(self, event: CalendarEvent):
        notification_intervals = [30, 15]
        dtstart = event.dtstart.astimezone(gettz())
        rrule = rrulestr(event.rrule, dtstart=dtstart) if event.rrule else None

        now = datetime.now(gettz())
        if rrule:
            next_occurrence = rrule.after(now)
            if next_occurrence is None:
                logger.info(f"No more occurrences for {event.summary}")
                return
            dtstart = next_occurrence
            dtend = dtstart + (event.dtend.astimezone(gettz()) - event.dtstart.astimezone(gettz()))
        else:
            dtend = event.dtend.astimezone(gettz())
        for interval in notification_intervals:
            notification_time = dtstart - timedelta(minutes=interval)
            self.scheduler_manager.add_job(
                job_function=self.notify_event,
                job_id=f"CAL_{event.summary} @ {dtstart} - {interval} minutes",
                trigger="date",
                run_date=notification_time,
                kwargs={"event": CalendarEvent(
                    summary=event.summary,
                    dtstart=dtstart,
                    dtend=dtend,
                    rrule=event.rrule,
                    location=event.location,
                    description=event.description
                )}
            )
            self.scheduler_manager.add_job(
                job_function=self.tts_engine.synthesize,
                job_id=f"CAL_TTS_NOTIFICATION_{event.summary} @ {dtstart} - {interval} minutes",
                trigger="date",
                run_date=notification_time,
                kwargs={"text": f"Event: {event.summary} starts in {interval} minutes"}
            )
        logger.info(f"Event scheduled: {event.summary} @ {dtstart}")
               
    def save_ics_calendar(self, file_path: str):
        """Save the calendar to an ics file.
        Args:
            file_path (str): The path to save the calendar to."""
        with open(file_path, "wb") as file:
            file.write(self.calendars.to_ical())
            
    def load_ics_file(self, file_path: str):
        """Load an ics file.
        Args:
            file_path (str): The path to the ics file."""
        with open(file_path, "rb") as file:
            self.calendars = Icalendar.from_ical(file.read())
            
    def get_events(self)->List[Dict[str, str]]:
        """Get all events from the calendar.
        Returns:
            List[Dict[str, str]]: A list of events."""
        events = []
        for component in self.calendars.walk("VEVENT"):
            rrule = component.get("rrule")
            rrule_str = rrule.to_ical().decode("utf-8") if rrule else None
            event = {
                "summary": str(component.get("summary")),
                "dtstart": component.get("dtstart").dt.strftime("%Y-%m-%d %H:%M:%S") if component.get("dtstart") else None,
                "dtend": component.get("dtend").dt.strftime("%Y-%m-%d %H:%M:%S") if component.get("dtend") else None,
                "rrule": rrule_str,
                "location": str(component.get("location", "")),
                "description": str(component.get("description", "")),
            }
            events.append(event)
        return events
    
    def get_today_events(self) -> List[Dict[str, str]]:
        """Get all events that are scheduled for today.
        Returns:
            List[Dict[str, str]]: A list of events that are scheduled for today.
        """
        events = self.get_events()
        today = datetime.combine(date.today(), datetime.min.time(), tzinfo=tzlocal())
        today_events: List[Dict[str, str]] = []
        for event in events:
            if event["dtstart"]:
                event_date = datetime.strptime(event["dtstart"], "%Y-%m-%d %H:%M:%S")
                if event_date.date() == today.date():
                    today_events.append(event)
                elif event["rrule"]:
                    dtstart = parse(event["dtstart"])
                    rrule_parts = event["rrule"].split(";")
                    rrule_dict = dict(pair.split("=") for pair in rrule_parts)
                    if "UNTIL" in rrule_dict:
                        until_dt = parse(rrule_dict["UNTIL"])
                        rrule_dict["UNTIL"] = until_dt.astimezone(gettz("UTC")).strftime("%Y%m%dT%H%M%SZ")
                    rrule_str = ";".join(f"{key}={value}" for key, value in rrule_dict.items())
                    rrule = rrulestr(rrule_str, dtstart=dtstart.astimezone(gettz("UTC")))
                    if rrule.between(datetime.combine(today, datetime.min.time(), tzinfo=tzlocal()), datetime.combine(today, datetime.max.time(), tzinfo=tzlocal())):
                        today_events.append(event)
        return today_events
