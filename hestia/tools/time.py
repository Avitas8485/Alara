from datetime import datetime
from dateutil.tz import gettz, tzlocal
from base_tool import Tool, ToolKit



class CurrentTimeTool(Tool):
    def __init__(self):
        self.name = "current_time"
        self.description = "Get current time"
        self.usage = "current_time"
        self.dependencies = {}
        
    def run(self)-> str:
        return datetime.now().strftime("%H:%M:%S")
    
class CurrentDateTool(Tool):
    def __init__(self):
        self.name = "current_date"
        self.description = "Get current date"
        self.usage = "current_date"
        self.dependencies = {}
        
    def run(self)-> str:
        return datetime.now().strftime("%d/%m/%Y")
    
class CurrentDatetimeTool(Tool):
    def __init__(self):
        self.name = "current_datetime"
        self.description = "Get current datetime"
        self.usage = "current_datetime"
        self.dependencies = {}
        
    def run(self)-> str:
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
class CurrentTimezoneTool(Tool):
    def __init__(self):
        self.name = "current_timezone"
        self.description = "Get current timezone"
        self.usage = "current_timezone"
        self.dependencies = {}
        
    def run(self) -> str:
        return str(datetime.now(tzlocal()).tzinfo)
    
class SetTimezoneTool(Tool):
    def __init__(self):
        self.name = "set_timezone"
        self.description = "Set the timezone"
        self.usage = "set_timezone [timezone]"
        self.dependencies = {}
        
    def run(self, timezone: str) -> str:
        return str(gettz(timezone))
    
class ToLocalTimeTool(Tool):
    def __init__(self):
        self.name = "to_local_time"
        self.description = "Convert time to local timezone"
        self.usage = "to_local_time [datetime]"
        self.dependencies = {}
        
    def run(self, dt: datetime) -> str:
        return str(dt.astimezone(tzlocal()))
    
class ToUtcTimeTool(Tool):
    def __init__(self):
        self.name = "to_utc_time"
        self.description = "Convert time to UTC timezone"
        self.usage = "to_utc_time [datetime]"
        self.dependencies = {}
        
    def run(self, dt: datetime) -> str:
        return str(dt.astimezone(gettz("UTC")))
    
class ToSystemTimezoneTool(Tool):
    def __init__(self):
        self.name = "to_system_timezone"
        self.description = "Convert time to system timezone"
        self.usage = "to_system_timezone [datetime]"
        self.dependencies = {}
        
    def run(self, dt: datetime) -> str:
        return str(dt.astimezone(tzlocal()))
    
class TimeDifferenceTool(Tool):
    def __init__(self):
        self.name = "time_difference"
        self.description = "Get the time difference between two datetime objects"
        self.usage = "time_difference [datetime1] [datetime2]"
        self.dependencies = {}
        
    def run(self, dt1: datetime, dt2: datetime) -> str:
        return str(dt1 - dt2)
    
class FormatTimeTool(Tool):
    def __init__(self):
        self.name = "format_time"
        self.description = "Format the time string"
        self.usage = "format_time [datetime] [format]"
        self.dependencies = {}
        
    def run(self, dt: datetime, format="%d/%m/%Y %H:%M:%S") -> str:
        return dt.strftime(format)
    
class ParseTimeTool(Tool):
    def __init__(self):
        self.name = "parse_time"
        self.description = "Parse the time string"
        self.usage = "parse_time [time_str] [format]"
        self.dependencies = {}
        
    def run(self, time_str: str, format="%d/%m/%Y %H:%M:%S") -> str:
        return str(datetime.strptime(time_str, format))
    
class TimeToolKit(ToolKit):
    def __init__(self):
        super().__init__()
        self.add_tool(CurrentTimeTool())
        self.add_tool(CurrentDateTool())
        self.add_tool(CurrentDatetimeTool())
        self.add_tool(CurrentTimezoneTool())
        self.add_tool(SetTimezoneTool())
        self.add_tool(ToLocalTimeTool())
        self.add_tool(ToUtcTimeTool())
        self.add_tool(ToSystemTimezoneTool())
        self.add_tool(TimeDifferenceTool())
        self.add_tool(FormatTimeTool())
        self.add_tool(ParseTimeTool())
        
    def __str__(self)-> str:
        return "\n".join([str(tool) for tool in self.tools.values()])
    
toolkit = TimeToolKit()
print(toolkit)

if __name__ == '__main__':
    # test the tools
    print(toolkit.run("current_time"))
    print(toolkit.run("current_date"))
    print(toolkit.run("current_datetime"))
    print(toolkit.run("current_timezone"))
    print(toolkit.run("set_timezone", "Asia/Kolkata"))
    print(toolkit.run("to_local_time", datetime.now()))
    print(toolkit.run("to_utc_time", datetime.now()))
    print(toolkit.run("to_system_timezone", datetime.now()))
    print(toolkit.run("time_difference", datetime.now(), datetime.now()))
    print(toolkit.run("format_time", datetime.now()))
    print(toolkit.run("parse_time", "01/01/2022 12:00:00"))
    