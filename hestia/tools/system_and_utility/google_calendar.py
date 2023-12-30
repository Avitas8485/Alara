import datetime
import os.path
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Constants
TOKEN_FILE = "token.json"
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CREDENTIALS_FILE = "HESTIA/hestia/tools/system_and_utility/credentials.json"
CALENDAR_SERVICE = "calendar"
CALENDAR_VERSION = "v3"

# Set up logging
logging.basicConfig(level=logging.INFO)

def get_credentials():
    creds = None
    try:
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    except (FileNotFoundError, OSError) as error:
        logging.error(f"Failed to load token file: {error}")
        return None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            except (FileNotFoundError, OSError) as error:
                logging.error(f"Failed to load credentials file: {error}")
                return None

        try:
            with open(TOKEN_FILE, "w") as token:
                token.write(creds.to_json())
        except OSError as error:
            logging.error(f"Failed to write token file: {error}")
            return None

    return creds

def get_events(service):
    now = datetime.datetime.utcnow().isoformat() + "Z"
    logging.info("Getting the upcoming 10 events")
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return events_result.get("items", [])

def print_events(events):
    if not events:
        logging.info("No upcoming events found.")
        return
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        logging.info(f"{start}, {event['summary']}")

def main():
    try:
        creds = get_credentials()
        if creds is None:
            return
        service = build(CALENDAR_SERVICE, CALENDAR_VERSION, credentials=creds)
        events = get_events(service)
        print_events(events)
    except Exception as error:
        logging.error(f"An error occurred: {type(error).__name__}, {error}")

if __name__ == "__main__":
    main()