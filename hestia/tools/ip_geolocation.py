import requests
import sys
from hestia.tools.base_tool import Tool, ToolKit

class IpAddressTool(Tool):
    def __init__(self):
        self.name = "ip_address"
        self.description = "Get the IP address of the system"
        self.usage = "ip_address"
        self.dependencies = {}
        
    def run(self):
        url = "https://api.ipify.org?format=json"
        response = requests.request("GET", url)
        ip_address = response.json()['ip']
        return ip_address
        
class IpInfoTool(Tool):
    def __init__(self):
        self.name = "ip_info"
        self.description = "Get basic information about an IP address"
        self.usage = "ip_info [ip_address]"
        self.dependencies = {"ip_address": IpAddressTool()}
        
    def run(self, ip_address: str= ""):
        # check dependencies
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