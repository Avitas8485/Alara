from typing import Tuple, Any

from transformers import pipeline
import json
from alara.lib.singleton import Singleton
from alara.lib.logger import logger
from alara.skills.skill_manager import SkillManager


class IntentRecognition(metaclass=Singleton):
    def __init__(self):
        """Initialize the intent recognition pipeline.
        The pipeline uses the zero-shot-classification model from the transformers library."""
        self.classifier = pipeline(task="zero-shot-classification", model="facebook/bart-large-mnli")
        self.skill_manager = SkillManager()
        self.intents = self.skill_manager.skill_mapping

    def classify_intent(self, text: str, intents, current_intent: dict, parent_intent=None) -> str:
        """Classify the intent of a given text.
        This function is recursive, and will classify the intent of a text based on the sub-intents of the current intent.
        Args:
            text (str): The text to classify.
            intents (dict): The intents dictionary.
            current_intent (dict): The current intent.
            parent_intent (str): The parent intent.
        Returns:
            str: The classified intent."""
        candidate_labels = [key["name"] for key in current_intent]
        result = self.classifier(text, candidate_labels)

        for key in current_intent:
            if result['labels'][0] == key["name"]:  # type: ignore
                if "features" in key:
                    return parent_intent, self.classify_intent(text, intents, key["features"],
                                                               key["name"])  # type: ignore
        logger.info(f"Intent: {parent_intent}, Sub-intent: {result['labels'][0]}")  # type: ignore
        return parent_intent, result['labels'][0]  # type: ignore

    def get_intent(self, text: str) -> str:
        """Get the intent of a given text.
        Args:
            text (str): The text to classify.
        Returns:
            str: The classified intent."""
        candidate_labels = [key for key in self.intents for key in self.intents[key]]
        general_intents = [key["name"] for key in candidate_labels]
        result = self.classifier(text, general_intents)

        for key in candidate_labels:
            if result['labels'][0] == key["name"]:  # type: ignore
                if "features" in key:
                    return self.classify_intent(text, self.intents, key["features"], key["name"])
        return result['labels'][0], None  # type: ignore
