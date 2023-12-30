import datetime
import os.path
import logging


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
TOKEN_FILE = "token.json"
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CREDENTIALS_FILE = "HESTIA/hestia/tools/system_and_utility/credentials.json"
CALENDAR_SERVICE = "calendar"
CALENDAR_VERSION = "v3"
class GoogleCalendar:
    def __init__(self):
        self.creds = self.get_credentials()
        if self.creds is not None:
            self.service = build(CALENDAR_SERVICE, CALENDAR_VERSION, credentials=self.creds)
        
    def load_credentials(self, file, scopes):
        try:
            if os.path.exists(file):
                return Credentials.from_authorized_user_file(file, scopes)
        except (FileNotFoundError, OSError) as error:
            logging.error(f"Failed to load file {file}: {error}")
            raise

    def get_credentials(self):
        creds = self.load_credentials(TOKEN_FILE, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                creds = self.load_credentials(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0) # type: ignore

            try:
                with open(TOKEN_FILE, "w") as token:
                    token.write(creds.to_json())
            except OSError as error:
                logging.error(f"Failed to write token file: {error}")
                raise

        return creds
    
    def get_all_calendars(self):
        page_token = None
        while True:
            calendar_list = self.service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list["items"]:
                logging.info(
                    f"{calendar_list_entry['summary']} - {calendar_list_entry['id']}"
                )
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
                logging.error(f"Failed to get events: {error}")
                return None
        return all_events
    
    def print_events(self, events):
        if not events:
            logging.info("No upcoming events found.")
            return
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            logging.info(f"{start}, {event['summary']}")
            
    def get_events_list(self):
        events = self.get_events()
        if events is not None:
            return events
        else:
            return None
        
    
if __name__ == "__main__":
    calendar = GoogleCalendar()
    events = calendar.get_events_list()
    calendar.print_events(events)