from alara.skills.skill_manager import Skill
import requests
import logging

logger = logging.getLogger(__name__)


class Advice(Skill):
    def __init__(self):
        self.skill_name = "advice"

    @Skill.skill_feature
    def get_advice(self) -> str:
        """Get advice from the Advice Slip API.
        Returns:
            str: The advice."""
        try:
            response = requests.get("https://api.adviceslip.com/advice")
            return response.json()["slip"]["advice"]
        except Exception as e:
            logger.error(f"Error getting advice: {e}")
            raise


def get_advice() -> str:
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