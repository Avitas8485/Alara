from alara.agent.agent import Agent

agent = Agent()
agent.run()



'''from hestia.nlp.intent_recognition import IntentRecognition
import json

intent_recognition = IntentRecognition()
intents = {'skills': [{'name': 'advice', 'features': [{'name': 'get_advice'}]}, {'name': 'alarm', 'features': [{'name': 'dismiss_alarm'}, {'name': 'snooze_alarm'}]}, {'name': 'mood_tracker', 'features': []}, {'name': 'news', 'features': [{'name': 'latest_news'}, {'name': 'news_in_category'}, {'name': 'top_news'}]}, {'name': 'weather', 'features': [{'name': 'current_weather'}]}]}
intent_recognition.intents = intents

print(intent_recognition.get_intent("What is the weather like in New York?")) # ('weather', 'current_weather')
print(intent_recognition.get_intent("What is the latest news?")) # ('news', 'latest_news')
'''