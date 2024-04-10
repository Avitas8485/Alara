from transformers import pipeline
import json
from hestia.lib.singleton import Singleton
from hestia.lib.hestia_logger import logger



class IntentRecognition(metaclass=Singleton):
    def __init__(self):
        self.classifier = pipeline(task="zero-shot-classification", model="facebook/bart-large-mnli")
        with open("hestia/nlp/intents.json", "r") as file:
            self.intents = json.load(file)
            
    def classify_intent(self, text: str, intents, current_intent: dict, parent_intent=None):
        candidate_labels = [key["name"] for key in current_intent]
        result = self.classifier(text, candidate_labels)

        for key in current_intent:
            if result['labels'][0] == key["name"]: # type: ignore
                if "sub_intents" in key:
                    return parent_intent, self.classify_intent(text, intents, key["sub_intents"], key["name"])
        logger.info(f"Intent: {parent_intent}, Sub-intent: {result['labels'][0]}") # type: ignore
        return parent_intent, result['labels'][0] # type: ignore
    
    def get_intent(self, text: str):
        candidate_labels = [key for key in self.intents for key in self.intents[key]]
        general_intents = [key["name"] for key in candidate_labels]
        result = self.classifier(text, general_intents)

        for key in candidate_labels:
            if result['labels'][0] == key["name"]: # type: ignore
                if "sub_intents" in key:
                    return self.classify_intent(text, self.intents, key["sub_intents"], key["name"])       
        return result['labels'][0], None # type: ignore
    


