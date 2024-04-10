from hestia.stt.whisper_stt import StreamHandler
from hestia.stt.wakeword import WakeWord
from hestia.nlp.intent_recognition import IntentRecognition
from hestia.skills.skill_manager import SkillManager
from hestia.lib.singleton import Singleton
from hestia.tts.piper_tts import PiperTTS
from hestia.llm.llama_chat_completion import LlamaChatCompletion
from hestia.tools.scheduler import SchedulerManager
import time


 
class Agent(metaclass=Singleton):
    def __init__(self):
        self.skill_manager = SkillManager()
        self.tts = PiperTTS()
        self.handler = StreamHandler()
        self.wake_word = WakeWord()
        self.intent_recognition = IntentRecognition()
        self.system_prompt = "Your name is Alara. You are an AI assistant that helps people with their daily tasks." 
        self.llm = LlamaChatCompletion()
        self.running = True
        self.scheduler = SchedulerManager()
        self.last_interaction = None
        
    def on_timeout(self):
        self.tts.synthesize("I'm sorry, I didn't catch that. Please try again.")
        # reset the last interaction time so that the agent can require the wake word to be detected
        self.last_interaction = None
     
    def process_user_prompt(self, user_prompt):
        intent, sub_intent = self.intent_recognition.get_intent(user_prompt)
        print(intent, sub_intent)
        try:
            self.skill_manager.call_skill(intent, sub_intent)
        except Exception as e:
            output = self.llm.chat_completion(system_prompt=self.system_prompt, user_prompt=f"Notify the user that the feature {sub_intent} has not been implemented yet.")
            self.tts.synthesize(output)
        self.last_interaction = time.time()   
    
    def run(self):
        while self.running:
            if self.last_interaction is not None and time.time() - self.last_interaction > 10:
                self.last_interaction = None
            if self.last_interaction is not None:
                user_prompt = self.handler.listen()
                if user_prompt:              
                    self.process_user_prompt(user_prompt)
            else:
                if self.wake_word.wake_word_detection():
                    self.last_interaction = time.time()
                    print("\033[96mWakeword detected..\033[0m")
                    self.tts.synthesize("How can I help you?")
                    user_prompt = self.handler.listen()
                    if user_prompt:
                        self.process_user_prompt(user_prompt)
                        
                    self.wake_word.clear_wakeword_buffer()
        
    def stop(self):
        self.running = False
        print("Agent stopped.")