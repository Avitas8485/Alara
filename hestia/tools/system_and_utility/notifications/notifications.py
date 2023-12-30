from plyer import notification

def notify(title, message, notification_type="reminder"):
    if notification_type == "reminder":
        app_icon = "HESTIA/hestia/tools/system_and_utility/notifications/icons/reminder.ico"
    notification.notify( # type: ignore
        title=title,
        message=message,
        app_icon=app_icon, # type: ignore
        timeout=30,
    )
    
if __name__ == "__main__":
    notify("Hello", "This is a test notification")