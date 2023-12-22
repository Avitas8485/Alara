import requests
import sys

def get_ip_address() -> str:
    """Returns IP address of the system"""
    url = "https://api.ipify.org?format=json"
    response = requests.request("GET", url)
    return response.json()['ip']

def get_geolocation(ip_address: str=None) -> dict:
    """Returns geolocation of the IP address"""
    if not ip_address:
        ip_address = get_ip_address()
    url = f"http://ip-api.com/json/{ip_address}"
    response = requests.request("GET", url)
    return response.json()


if __name__ == '__main__':
    ip_address = sys.argv[1] if len(sys.argv) > 1 else None
    geolocation = get_geolocation(ip_address)
    print(f"""Geolocation for {geolocation['query']}:
    Country: {geolocation['country']}
    City: {geolocation['city']}
    Zip code: {geolocation['zip']}
    Latitude: {geolocation['lat']}
    Longitude: {geolocation['lon']}
    ISP: {geolocation['isp']}
    Organization: {geolocation['org']}
    Timezone: {geolocation['timezone']}
    """)