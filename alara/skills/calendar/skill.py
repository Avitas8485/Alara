import requests
from icalendar import Calendar as Icalendar
from icalendar import Event, vDatetime, vRecur
from datetime import datetime, date
from dateutil.rrule import rrulestr
from dateutil.parser import parse
from dateutil.tz import gettz, tzlocal
from typing import List, Dict, Optional, Any
import os

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
                dtstart: datetime=datetime.now(),
                dtend: datetime=datetime.now(),
                rrule: Optional[str] = None,
                location: Optional[str] = None,
                description: Optional[str] = None):
        self.summary = summary
        self.dtstart = dtstart
        self.dtend = dtend
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
    
     


        
    

class Calendar:
    def __init__(self):
        self.calendars = Icalendar()
        
        
        
    def load_links_from_file(self, file_path: str='alara/skills/calendar/ics_links.txt'):
        """Load calendar links from a file.
        Args:
            file_path (str): The path to the file containing calendar links."""
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist.")
            return
        with open(file_path, "r") as file:
            for line in file:
                self.load_ics_calendar(line.strip())
        
    def load_ics_calendar(self, url: str):
        """Load an ics calendar from a URL.
        Args:
            url (str): The URL of the calendar.
            Returns:
                None."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            calendar = Icalendar.from_ical(response.text)
            for component in calendar.walk("VEVENT"):
                self.calendars.add_component(component)
        except requests.exceptions.HTTPError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error: {e}")
    
    def add_event(self, event: CalendarEvent):
        """Add an event to the calendar.
        Args:
            event (CalendarEvent): The event to add to the calendar.
            Returns:
                None."""
        if not event._validate_event():
            return
        self.calendars.add_component(event.to_event())            
    
    
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
        component = self.fetch_event(event.summary)  
        if component:
            component.set("summary", event.summary)
            component.set("dtstart", vDatetime(event.dtstart))
            component.set("dtend", vDatetime(event.dtend))
            if event.rrule:
                component.set("rrule", vRecur.from_ical(event.rrule))
            if event.location:
                component.set("location", event.location)
            if event.description:
                component.set("description", event.description)
    
    
    
    def delete_event(self, event: CalendarEvent):
        component = self.fetch_event(event.summary)
        if component:
            self.calendars.subcomponents.remove(component)
    
            
               
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
    
    
    
    
    
        



    
    
