from transformers import pipeline
import json

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
with open("hestia/nlp/intents.json", "r") as file:
        intents = json.load(file)

def classify_intent(text, intents, current_intent):
    candidate_labels = [key["name"] for key in current_intent]
    result = classifier(text, candidate_labels)

    for key in current_intent:
        if result['labels'][0] == key["name"]: # type: ignore
            if "sub_intents" in key:
                return classify_intent(text, intents, key["sub_intents"])
    return result['labels'][0] # type: ignore

def get_intent(text):
    
    candidate_labels = [key for key in intents for key in intents[key]]
    general_intents = [key["name"] for key in candidate_labels]
    result = classifier(text, general_intents)

    for key in candidate_labels:
        if result['labels'][0] == key["name"]: # type: ignore
            if "sub_intents" in key:
                return classify_intent(text, intents, key["sub_intents"])
    return result['labels'][0] # type: ignore
    
    

# Example usage
list_of_texts = [
    "What day is it today?",
    "What is the time?",
    "Remind me to buy some milk",
    "Set a timer for 10 minutes",
    "What plans do I have for today?",
    "Send an email to John",
    "What is the capital of France?",
    "Can you explain the concept of gravity?",
]
for text in list_of_texts:
    print(get_intent(text))
    print("----")
    
