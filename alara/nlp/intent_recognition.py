from transformers import pipeline
from alara.lib.singleton import Singleton
from alara.lib.logger import logger
from alara.skills.skill_manager import SkillManager


class IntentRecognition(metaclass=Singleton):
    def __init__(self, skill_manager: SkillManager):
        """Initialize the intent recognition pipeline.
        The pipeline uses the zero-shot-classification model from the transformers library.
        Args:
            skill_manager (SkillManager): The skill manager to use for intent recognition."""
        self.classifier = pipeline(task="zero-shot-classification", model="MoritzLaurer/deberta-v3-large-zeroshot-v2.0") # TODO: Get better model
        self.skill_manager = skill_manager
        self.intents = self.skill_manager.skill_mapping
        logger.info("Intent recognition initialized.")

    def get_intent(self, text: str) -> str:
        """Get the intent of a given text.
        Args:
            text (str): The text to classify.
        Returns:
            str: The classified intent."""
        candidate_labels = [key for key in self.intents for key in self.intents[key]]
        general_intents = [key["name"] for key in candidate_labels]
        result = self.classifier(text, general_intents)
        return result['labels'][0]  # type: ignore
