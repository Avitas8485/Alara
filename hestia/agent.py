from hestia.stt.whisper_stt import StreamHandler
from hestia.stt.wakeword import WakeWord
from hestia.nlp.intent_recognition import IntentRecognition
from hestia.skills.skill_manager import SkillManager
from hestia.lib.singleton import Singleton
from hestia.tts.piper_tts import PiperTTS
from hestia.llm.llama_chat_completion import LlamaChatCompletion
from hestia.tools.scheduler import SchedulerManager



# implementation a loop to keep the program running

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
        
        
    def run(self):
        while self.running:
            if self.wake_word.wake_word_detection():
                print("\033[96mWakeword detected..\033[0m")
                user_prompt = self.handler.listen()
                
                if user_prompt is None:
                    user_prompt = ''
                intent, sub_intent = self.intent_recognition.get_intent(user_prompt)
                print(intent, sub_intent)
                try:
                    self.skill_manager.call_skill(intent, sub_intent)
                except Exception as e:
                    output = self.llm.chat_completion(system_prompt=self.system_prompt, user_prompt="Notify the user that the feature has not been implemented yet.")
                    self.tts.synthesize(output)
                self.wake_word.clear_wakeword_buffer()
                
    def stop(self):
        self.running = False
        print("Agent stopped.")