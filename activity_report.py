import os
import socket
from datetime import datetime, timedelta, time

import iso8601
import pandas as pd
from aw_client import ActivityWatchClient
from aw_client.classes import default_classes
from aw_client.queries import DesktopQueryParams, canonicalEvents
from hestia.tools.system_and_utility.ip_geolocation import get_geolocation
from pytz import timezone
from hestia.llm.llama_chat_completion import chat_completion, load_prompt
from hestia.text_to_speech.speech import TextToSpeechSystem
from hestia.tools.reports.base_report_generator import BaseReportGenerator

class ActivityReportGenerator(BaseReportGenerator):
    def __init__(self):
        self.todays_date = datetime.now().strftime("%b %d, %Y")
        self.DIR_PATH = "hestia/tools/reports/activity"
        self.activity_report_path = os.path.join(self.DIR_PATH, f"activity_report {self.todays_date}.txt")
        self.simplified_activity_path = os.path.join(self.DIR_PATH, f"{self.todays_date}activity_report.txt")
        self.hostname = "fakedata" if os.getenv("CI") else socket.gethostname()
        self.aw = ActivityWatchClient()
        self.timezone = self.get_timezone()
        
    def write_file(self, file_path: str, content):
        """Write to a file.
        Args:
            file_path: The path to the file.
            content: The content to write to the file."""
        with open(file_path, "w") as f:
            f.write(content)
            
    def read_file(self, file_path: str)->str:
        """Read a file.
        Args:
            file_path: The path to the file.
        Returns:
            str: The content of the file."""
        with open(file_path, "r") as f:
            return f.read()
    def get_timezone(self) -> str:
        """Returns timezone of the system"""
        geolocation = get_geolocation()
        return geolocation['timezone']
    def get_start_of_day(self, now: datetime):
        start_of_day = now.replace(hour=4, minute=0, second=0, microsecond=0)
        if now < start_of_day:
            start_of_day -= timedelta(days=1)
        return start_of_day
    
    def build_query(self) -> str:
        canonicalQuery = canonicalEvents(
            DesktopQueryParams(
                bid_window=f"aw-watcher-window_{self.hostname}",
                bid_afk=f"aw-watcher-afk_{self.hostname}",
                classes=default_classes,
            )
        )
        return f"""
        {canonicalQuery}
        RETURN = {{"events": events}};
        """
        
    def get_activity_summary(self) -> str:
        """Returns activity summary"""
        now = datetime.now(tz=timezone(self.timezone))
        start_of_day = self.get_start_of_day(now)
        bucket_id = f"aw-watcher-afk_{self.hostname}"
        events = self.aw.get_events(bucket_id, start=start_of_day, end=now)
        events = [e for e in events if e.data["status"] == "not-afk"]
        total_duration = sum((e.duration for e in events), timedelta())
        return f"Total time spent on computer today: {total_duration}"
        
    def get_information(self):
        """Returns activity data
        Returns:
            dict: The activity data."""
        now = datetime.now(tz=timezone(self.timezone))
        start_of_day = self.get_start_of_day(now)
        query = self.build_query()
        data = self.aw.query(query, [(start_of_day, now)])
        events = [
        {
            "timestamp": e["timestamp"],
            "duration": timedelta(seconds=e["duration"]),
            **e["data"],
        }
        for e in data[0]["events"]
    ]
        for e in events:
            e["$category"] = " > ".join(e["$category"])

        df = pd.json_normalize(events)
        df["timestamp"] = pd.to_datetime(df["timestamp"].apply(lambda x: iso8601.parse_date(x).astimezone(timezone(self.timezone))))
        df['date'] = df['timestamp'].dt.date
        df['time'] = df['timestamp'].dt.time
        df['duration'] = df['duration'].dt.total_seconds()
        df['duration'] = df['duration'].astype(int)
        df['duration'] = pd.to_timedelta(df['duration'], unit='s')
    
        df = df[['date', 'time', 'duration', '$category', 'title', 'app']] # rearrange columns
        
        
        return df
    
    def parse_information(self):
        df = self.get_information()
        
        most_used_app = df['app'].value_counts().idxmax()
        most_used_app_category = df[df['app'] == most_used_app]['$category'].value_counts().idxmax()
        most_used_category = df['$category'].value_counts().idxmax()
        activity_summary = self.get_activity_summary()
        
        info = f"""Activity report for {self.todays_date}:\n
        {activity_summary}\n
        Most used app: {most_used_app} ({most_used_app_category})\n
        Most used category: {most_used_category}"""
        self.write_file(self.simplified_activity_path, info)
        
    def generate_report_summary(self):
        """Generate the activity report summary."""
        activity = self.read_file(self.simplified_activity_path)
        activity_prompt = load_prompt(prompt_name="activity_report")
        activity_summary = chat_completion(system_prompt=activity_prompt, user_prompt=f"Activity summary for {self.todays_date}:\n\n{activity}")
        self.write_file(self.activity_report_path, activity_summary)
        
    
    def convert_summary_to_audio(self):
        """Convert the summary to audio."""
        activity = self.read_file(self.activity_report_path)
        tts = TextToSpeechSystem()
        if activity is None:
            return
        tts.convert_text_to_speech(
            text=activity,
            output_dir='hestia/text_to_speech/outputs/activity_report',
            output_filename=f"{self.todays_date}activity_report")
        
        
        
        
        
        
        
if __name__ == "__main__":
    activity_report_generator = ActivityReportGenerator()
    activity_report_generator.parse_information()
    activity_report_generator.generate_report_summary()
    activity_report_generator.convert_summary_to_audio()
    