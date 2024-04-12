import requests
from hestia.tools.base_tool import Tool, ToolKit

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
        self.healthy = self.check_health()
        
    def check_health(self)-> bool:
        try:
            requests.request("GET", "https://www.google.com")
            return True
        except requests.exceptions.ConnectionError:
            return False
        
    def run(self)-> bool:
        """Returns True if the internet connection is available, False otherwise
        Returns:
            bool: True if the internet connection is available, False otherwise"""
        try:
            requests.request("GET", "https://www.google.com")
            return True
        except requests.exceptions.ConnectionError:
            return False

    
if __name__ == '__main__':
    internet_connection_tool = InternetConnectionTool()
    print(internet_connection_tool.run())
    