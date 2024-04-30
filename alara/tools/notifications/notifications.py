from plyer import notification
from typing import Optional
from enum import Enum
from alara.tools.base_tool import Tool, ToolStatus
import pyaudio
import wave
from typing import Optional, Dict

        
class NotificationType(Enum):
    REMINDER = "reminder"
    ALARM_CLOCK = "alarm_clock"
    CALENDAR = "calendar"
    
class NotificationTool(Tool):
    """Tool to send a notification to the user
    Attributes:
        name: str: The name of the tool
        description: str: The description of the tool
        usage: str: The usage of the tool
        dependencies: dict: The dependencies of the tool
        status: ToolStatus: The status of the tool"""
        
    def __init__(self):
        self.name = "notification"
        self.description = "Send a notification to the user"
        self.usage = "notification [title] [message] [type]"
        self.status = ToolStatus.UNKNOWN
        self.dependencies = {}
        self.icon_mapping: Dict[NotificationType, str] = {
            NotificationType.REMINDER: "alara/tools/notifications/icons/reminder.ico",
            NotificationType.ALARM_CLOCK: "alara/tools/notifications/icons/alarm_clock.ico",
            NotificationType.CALENDAR: "alara/tools/notifications/icons/calendar.ico"
        }
        
        
    def _run(self, title: str='', message: str='', notification_type: Optional[NotificationType]= NotificationType.REMINDER)-> None:
        """Send a notification to the user
        Args:
            title: str: The title of the notification
            message: str: The message of the notification
            notification_type: NotificationType: The type of the notification"""
        app_icon = self.icon_mapping.get(notification_type if notification_type else NotificationType.REMINDER)
        notification.notify( # type: ignore
            title=title,
            message=message,
            app_icon=app_icon,
            app_name="Alara",
            ticker=title,
            timeout=30
        )
        self.play_audio("alara/tools/sounds/system-notification-199277.wav")

    def play_audio(self, audio_path):
            """Play the audio."""   
            chunk = 1024
            try:
                with wave.open(audio_path, 'rb') as wf:
                    p = pyaudio.PyAudio()
                    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                                channels=wf.getnchannels(),
                                rate=wf.getframerate(),
                                output=True)
                    data = wf.readframes(chunk)
                    while len(data) > 0:
                        stream.write(data)
                        data = wf.readframes(chunk)
                    stream.close()
            except Exception as e:
                print(f"Error: {e}")
        
    
if __name__ == "__main__":
    notification_tool = NotificationTool()
    notification_tool._run("Test", "This is a test notification")