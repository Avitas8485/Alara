from plyer import notification
from typing import Optional
from enum import Enum

class NotificationType(Enum):
    REMINDER = "reminder"
    

def notify(title: str, message: str, notification_type: Optional[NotificationType] = NotificationType.REMINDER)-> None:
    if notification_type == NotificationType.REMINDER:
        app_icon = "alara/tools/notifications/icons/reminder.ico"
    notification.notify( # type: ignore
        title=title,
        message=message,
        app_icon=app_icon, # type: ignore
        timeout=30,
    )
    
if __name__ == "__main__":
    notify("Hello", "This is a test notification")