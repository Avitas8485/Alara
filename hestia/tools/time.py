from datetime import datetime
from dateutil.tz import gettz, tzlocal
from ip_geolocation import get_geolocation

def default_timezone():
    return gettz(get_geolocation()['timezone'])


def set_timezone(timezone):
    return gettz(timezone)

def to_timezone(dt: datetime, tz):
    """Convert a datetime object to a specified timezone."""
    if dt.tzinfo:
        return dt.astimezone(tz)
    else:
        return dt.replace(tzinfo=tz).astimezone(tz)

def to_utc(dt):
    """Convert a datetime object to UTC timezone."""
    tzUTC = gettz("UTC")
    return to_timezone(dt, tzUTC)

def now_utc():
    """Return the current time in UTC timezone."""
    return to_utc(datetime.utcnow())
   
def to_local(dt):
    """Convert a datetime object to the local timezone."""
    tz = default_timezone()
    return to_timezone(dt, tz)
    

def to_system_timezone(dt):
    """Convert a datetime object to the system's local timezone."""
    tz = tzlocal()
    return to_timezone(dt, tz)