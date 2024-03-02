from hestia.skills.reports.base_report_generator import BaseReportGenerator
from hestia.llm.llama_chat_completion import LlamaChatCompletion, load_prompt_txt as load_prompt
from hestia.tts.xtts_tts import XttsTTS as TextToSpeechSystem
from hestia.skills.google_calendar import GoogleCalendar
from datetime import datetime
import os
import unicodedata
from hestia.config.config import cfg

class ScheduleReport(BaseReportGenerator):
    def __init__(self):
        self.summary_path = os.path.join(cfg.REPORT_SUMMARY_PATH, f"summary.txt")
        self.todays_date = datetime.now().strftime("%b %d, %Y")
        self.llm = LlamaChatCompletion()
    
    def remove_non_ascii(self, text: str)->str:
        """Remove non-ascii characters from text.
        Args:
            text: The text to remove non-ascii characters from.
        Returns:
            str: The text with non-ascii characters removed."""
        return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        
    def write_file(self, file_path: str, content):
        """Write to a file.
        Args:
            file_path: The path to the file.
            content: The content to write to the file."""
        content = self.remove_non_ascii(content)
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
        
    def get_information(self):
        """Get the schedule for today."""
        calendar = GoogleCalendar()
        events = calendar.get_events_for_today()
        return events
        
    
    def parse_information(self):
        """Parse the schedule for today."""
        events = self.get_information()
        schedule_report = ""
        for event in events:
            # check if the event is all day or for a specific time
            if "dateTime" in event["start"]:
                start = event["start"]["dateTime"]
                end = event["end"]["dateTime"]
                summary = event["summary"]
                schedule_report += f"{start} to {end}: {summary}\n"
            else:
                summary = event["summary"]
                schedule_report += f"All day: {summary}\n"
        return schedule_report

    
    def generate_report_summary(self):
        """Generate a schedule report."""
        schedule = self.parse_information()
        schedule_prompt = load_prompt("schedule_report")
        schedule_summary = self.llm.chat_completion(system_prompt=schedule_prompt, user_prompt=f"Beginning of schedule\n\nSchedule for {self.todays_date}: [{schedule}]\n\nEnd of schedule.")
        self.write_file(self.summary_path, schedule_summary)
        
    
    def convert_summary_to_audio(self):
        """Convert the summary to audio."""
        schedule = self.read_file(self.summary_path)
        tts = TextToSpeechSystem()
        if schedule is None:
            return  # no schedule for today
        tts.synthesize_to_file(
            text=schedule,
            output_dir='hestia/text_to_speech/outputs/schedule_report',
            output_filename=f"{self.todays_date}schedule_report")
        
        

        
        