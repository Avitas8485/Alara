import requests
#from hestia.lib.hestia_logger import logger
import logging
logger = logging.getLogger(__name__)


def get_advice():
    """Get advice from the Advice Slip API.
    Returns:
        str: The advice."""
    try:
        response = requests.get("https://api.adviceslip.com/advice")
        return response.json()["slip"]["advice"]
    except Exception as e:
        logger.error(f"Error getting advice: {e}")
        raise


def main():
    """Get advice from the Advice Slip API."""
    print(get_advice())
    
if __name__ == "__main__":
    main()