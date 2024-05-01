import requests
from alara.tools.base_tool import Tool, ToolKit, ToolStatus

class InternetConnectionTool(Tool):
    """Tool to check the internet connection
    Attributes:
        name: str: The name of the tool
        description: str: The description of the tool
        usage: str: The usage of the tool
        dependencies: dict: The dependencies of the tool"""
    def __init__(self):
        self.name = "internet_connection"
        self.description = "Check the internet connection"
        self.usage = "internet_connection"
        self.dependencies = {}
        self.status = ToolStatus.UNKNOWN
        
            
        
    def _run(self)-> bool:
        """Returns True if the internet connection is available, False otherwise
        Returns:
            bool: True if the internet connection is available, False otherwise"""
        try:
            requests.request("GET", "https://www.google.com")
            return True
        except requests.exceptions.ConnectionError:
            self.status = ToolStatus.UNHEALTHY
            return False

    
if __name__ == '__main__':
    internet_connection_tool = InternetConnectionTool()
    print(internet_connection_tool.run())
    