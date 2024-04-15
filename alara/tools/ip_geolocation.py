import requests
import sys
from alara.tools.base_tool import Tool, ToolKit
from alara.tools.internet_connection import InternetConnectionTool

class IpAddressTool(Tool):
    """Tool to get the IP address of the system
    Attributes:
        name: str: The name of the tool
        description: str: The description of the tool
        usage: str: The usage of the tool
        dependencies: dict: The dependencies of the tool"""
    def __init__(self):
        self.name = "ip_address"
        self.description = "Get the IP address of the system"
        self.usage = "ip_address"
        self.dependencies = {"internet_connection": InternetConnectionTool()}
        self.healthy = self.check_health()
        
    def check_health(self)-> bool:
        url = "https://api.ipify.org?format=json"
        try:
            requests.request("GET", url)
            return True
        except Exception as e:
            print(f"Error checking health of {self.name}: {e}")
            return False
        
        
    def run(self)-> str:
        """Returns the IP address of the system
        Returns:
            str: The IP address of the system"""
        url = "https://api.ipify.org?format=json"
        response = requests.request("GET", url)
        ip_address = response.json()['ip']
        return ip_address
        
class IpInfoTool(Tool):
    """Tool to get information about an IP address
    Attributes:
        name: str: The name of the tool
        description: str: The description of the tool
        usage: str: The usage of the tool
        dependencies: dict: The dependencies of the tool"""
    def __init__(self):
        self.name = "ip_info"
        self.description = "Get basic information about an IP address"
        self.usage = "ip_info [ip_address]"
        self.dependencies = {"ip_address": IpAddressTool()}
        self.healthy = self.check_health()
        
    def check_health(self)-> bool:
        self.dependencies['ip_address'].check_health()
        return self.dependencies['ip_address'].healthy
        
        
    def run(self, ip_address: str= "")-> dict:
        """Returns the geolocation of the IP address
        Args:
            ip_address: str: The IP address to get the geolocation of
        Returns:
            dict: The geolocation of the IP address"""
        if ip_address == "":
            ip_address = self.dependencies['ip_address'].run()
        url = f"http://ip-api.com/json/{ip_address}"
        response = requests.request("GET", url)
        geolocation = response.json()
        return geolocation

class IpGeolocationToolKit(ToolKit):
    def __init__(self):
        super().__init__()
        self.add_tool(IpAddressTool())
        self.add_tool(IpInfoTool())
        
    def __str__(self)-> str:
        return "\n".join([str(tool) for tool in self.tools.values()])
    
    def run(self, tool_name: str, *args, **kwargs):
        if self.check_dependencies(tool_name):
            tool = self.tools[tool_name]
            return tool.run(*args, **kwargs)
        else:
            print(f"Error running tool: {tool_name}")
'''
toolkit = ToolKit()
toolkit.add_tool(IpAddressTool())
toolkit.add_tool(IpInfoTool())
print(toolkit)

if __name__ == '__main__':
    # test the tools
    toolkit.run("ip_address", [])
    toolkit.run("ip_info", [])
    
    
 
  

def get_ip_address() -> str:
    """Returns IP address of the system"""
    url = "https://api.ipify.org?format=json"
    response = requests.request("GET", url)
    return response.json()['ip']

def get_geolocation(ip_address: str = "") -> dict:
    """Returns geolocation of the IP address"""
    if not ip_address:
        ip_address = get_ip_address()
    url = f"http://ip-api.com/json/{ip_address}"
    response = requests.request("GET", url)
    return response.json()


if __name__ == '__main__':
    ip_address = sys.argv[1] if len(sys.argv) > 1 else None
    geolocation = get_geolocation(ip_address or "")
    print(f"""Geolocation for {geolocation['query']}:
    Country: {geolocation['country']}
    City: {geolocation['city']}
    Zip code: {geolocation['zip']}
    Latitude: {geolocation['lat']}
    Longitude: {geolocation['lon']}
    ISP: {geolocation['isp']}
    Organization: {geolocation['org']}
    Timezone: {geolocation['timezone']}
    """)'''