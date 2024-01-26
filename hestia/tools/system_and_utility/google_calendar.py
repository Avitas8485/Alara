import datetime
import os.path
import logging
import threading
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from hestia.lib.hestia_logger import logger


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

TOKEN_FILE = "C:/Users/avity/Projects/credentials/googel_cal/token.json"
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CREDENTIALS_FILE = "C:/Users/avity/Projects/credentials/googel_cal/credentials.json"
CREDENTIALS_FILE = "C:/Users/avity/Projects/credentials/googel_cal/credentials.json"
CALENDAR_SERVICE = "calendar"
CALENDAR_VERSION = "v3"


class GoogleCalendar:
    def __init__(self):
        self.lock = threading.Lock()
        self.events = []
        self.creds = self.get_credentials()
        if self.creds is not None:
            self.service = build(CALENDAR_SERVICE, CALENDAR_VERSION, credentials=self.creds)
        #self.update_events()
        
        
    def load_credentials(self, file, scopes):
        try:
            if os.path.exists(file):
                return Credentials.from_authorized_user_file(file, scopes)
        except (FileNotFoundError, OSError) as error:
            logger.error(f"Failed to load credentials: {error}")
            return None
    
    def refresh_credentials(self, creds):
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0) # type: ignore
        return creds
    
    def get_credentials(self):
        creds = self.load_credentials(TOKEN_FILE, SCOPES)

        if not creds or not creds.valid:
            creds = self.refresh_credentials(creds)
            
            try:
                with open(TOKEN_FILE, "w") as token:
                    token.write(creds.to_json())
            except OSError as error:
                logger.error(f"Failed to write credentials: {error}")
                return None

        return creds
    
    def get_all_calendars(self):
        page_token = None
        while True:
            calendar_list = self.service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list["items"]:
                logger.info(f"{calendar_list_entry['summary']}, {calendar_list_entry['id']}")
                yield calendar_list_entry['id']
            page_token = calendar_list.get("nextPageToken")
            if not page_token:
                break
            
    def get_events(self):
        now = datetime.datetime.utcnow().isoformat() + "Z"
        logging.info("Getting the upcoming 10 events")
        all_events = []
        for calendar_id in self.get_all_calendars():
            try:
                events_result = (
                    self.service.events()
                    .list(
                        calendarId=calendar_id,
                        timeMin=now,
                        maxResults=10,
                        singleEvents=True,
                        orderBy="startTime",
                    )
                    .execute()
                )
                all_events.extend(events_result.get("items", []))
            except HttpError as error:
                logger.error(f"Failed to get events: {error}")
                raise
        return all_events
    
    def get_events_for_today(self):
        today = datetime.datetime.utcnow().date().isoformat() + "T00:00:00Z"
        tomorrow = (datetime.datetime.utcnow().date() + datetime.timedelta(days=1)).isoformat() + "T00:00:00Z"
        logging.info("Getting today's events")
        all_events = []
        for calendar_id in self.get_all_calendars():
            try:
                events_result = (
                    self.service.events()
                    .list(
                        calendarId=calendar_id,
                        timeMin=today,
                        timeMax=tomorrow,
                        singleEvents=True,
                        orderBy="startTime",
                    )
                    .execute()
                )
                all_events.extend(events_result.get("items", []))
            except HttpError as error:
                logging.error(f"Failed to get events: {error}")
                raise
        return all_events
        
        
    
    def print_events(self, events):
        if not events:
            logger.info("No upcoming events found.")
            return
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            logger.info(f"{start} - {event['summary']}")
            
    def get_events_list(self):
        with self.lock:
            events = self.get_events()
            if events is not None:
                return events
            else:
                return []
            
        
    def update_events(self):
        with self.lock:
            self.events = self.get_events_list()
            

    
if __name__ == "__main__":
    calendar = GoogleCalendar()
    from datetime import timedelta
    events = calendar.get_events_list()
    for event in events:
        # check if the event has a time associated with it
        if "dateTime" in event["start"]:
            event_start = datetime.datetime.fromisoformat(event["start"]["dateTime"])
            notification_time = event_start - timedelta(minutes=60)
            print(notification_time)
            print(event["summary"])
            print(event["start"])
            print(event["end"])
            print()
        else:
            print("all day event")
            print(event["summary"])
            print(event["start"])
            print(event["end"])
            print()
    today_events = calendar.get_events_for_today()
    for event in today_events:
        # check if the event has a time associated with it
        if "dateTime" in event["start"]:
            event_start = datetime.datetime.fromisoformat(event["start"]["dateTime"])
            notification_time = event_start - timedelta(minutes=60)
            print(notification_time)
            print(event["summary"])
            print(event["start"])
            print(event["end"])
            print()
        else:
            print("all day event")
            print(event["summary"])
            print(event["start"])
            print(event["end"])
            print()