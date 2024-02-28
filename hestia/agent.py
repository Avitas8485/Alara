from hestia.stt.whisper_stt import StreamHandler
from hestia.stt.wakeword import WakeWord
from hestia.nlp.intent_recognition import IntentRecognition
from hestia.skills.skill_manager import SkillManager
from hestia.lib.singleton import Singleton
from hestia.tts.piper_tts import PiperTTS
from hestia.llm.llama_chat_completion import LlamaChatCompletion

handler = StreamHandler()
wake_word = WakeWord()
intent_recognition = IntentRecognition()

# implementation a loop to keep the program running

class Agent(metaclass=Singleton):
    def __init__(self) -> None:
        self.skill_manager = SkillManager()
        self.handler = StreamHandler()
        self.wake_word = WakeWord()
        self.intent_recognition = IntentRecognition()
        self.system_prompt = "Your name is Alara. You are an AI assistant that helps people with their daily tasks." 
        self.tts = PiperTTS()
        self.llm = LlamaChatCompletion()
        
    def run(self):
        while True:
            if self.wake_word.wake_word_detection():
                print("\033[96mWakeword detected..\033[0m")
                user_prompt = self.handler.listen()
                
                if user_prompt is None:
                    user_prompt = ''
                intent, sub_intent = self.intent_recognition.get_intent(user_prompt)
                print(intent, sub_intent)
                self.skill_manager.call_skill(intent, sub_intent)
                self.wake_word.clear_wakeword_buffer()
                
agent = Agent()
agent.run()