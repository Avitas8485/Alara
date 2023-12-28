from plyer import notification

def notify(title, message):
    notification.notify( # type: ignore
        title=title,
        message=message,
        app_icon=None,
        timeout=10,
    )
    
if __name__ == "__main__":
    notify("Hello", "This is a test notification")