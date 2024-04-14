from hestia.stt.whisper_stt import StreamHandler
from hestia.stt.wakeword import WakeWord
from hestia.nlp.intent_recognition import IntentRecognition
from hestia.skills.skill_manager import SkillManager
from hestia.lib.singleton import Singleton
from hestia.tts.piper_tts import PiperTTS
from hestia.llm.llama_chat_completion import LlamaChatCompletion
from hestia.tools.scheduler import SchedulerManager
from hestia.automation.automation_handler import AutomationHandler
from hestia.automation.event import Event, State
from hestia.lib.hestia_logger import HestiaLogger
import time


class Agent(metaclass=Singleton):
    def __init__(self):
        
        self.tts = PiperTTS()
        self.stream_handler = StreamHandler()
        self.wake_word = WakeWord()
        self.intent_recognition = IntentRecognition()
        self.system_prompt = "Your name is Alara. You are an AI assistant that helps people with their daily tasks."
        self.skill_manager = SkillManager()
        self.llm = LlamaChatCompletion()
        self.running = True
        self.scheduler = SchedulerManager()
        self.automation_handler = AutomationHandler()
        self.last_interaction = None
        self.agent_name = "Alara"
        self.agent_state = None
        self.logger = HestiaLogger("Alara").logger
        self.agent_state = self.automation_handler.state_machine.add_state(
            State(entity_id=self.agent_name, state="idle", attributes={"last_interaction": None}))

    def on_timeout(self):
        self.tts.synthesize("I'm sorry, I didn't catch that. Please try again.")
        # reset the last interaction time so that the agent can require the wake word to be detected
        self.last_interaction = None

    def process_user_prompt(self, user_prompt):
        self.logger.debug(f"User prompt: {user_prompt}")
        self.automation_handler.state_machine.set_state(entity_id=self.agent_name, new_state="processing",
                                                        attributes={"last_interaction": self.last_interaction})
        intent, sub_intent = self.intent_recognition.get_intent(user_prompt)
        self.logger.debug(f"Intent: {intent}, Sub-intent: {sub_intent}")
        try:
            self.skill_manager.call_feature(sub_intent)
        except Exception as e:
            self.logger.error(f"Error calling skill: {e}")
            output = self.llm.chat_completion(system_prompt=self.system_prompt,
                                              user_prompt=f"Notify the user that the feature {sub_intent} has not been implemented yet.")
            self.tts.synthesize(output)
        self.last_interaction = time.time()

    def handle_wakeword(self):
        self.last_interaction = time.time()
        self.logger.info("Wakeword detected.")
        self.automation_handler.event_bus.emit_event(Event("wakeword_detected", {"agent_name": self.agent_name}))
        self.automation_handler.state_machine.set_state(entity_id=self.agent_name, new_state="listening",
                                                        attributes={"last_interaction": self.last_interaction})
        self.tts.synthesize("How can I help you?")
        user_prompt = self.stream_handler.listen()
        if user_prompt:
            self.process_user_prompt(user_prompt)
        self.wake_word.clear_wakeword_buffer()

    def run(self):
        while self.running:
            if self.last_interaction is not None and time.time() - self.last_interaction > 10:
                self.automation_handler.event_bus.emit_event(Event("idle", {"agent_name": self.agent_name}))
                self.automation_handler.state_machine.set_state(entity_id=self.agent_name, new_state="idle",
                                                                attributes={"last_interaction": None})
                self.last_interaction = None
            if self.last_interaction is not None:
                user_prompt = self.stream_handler.listen()
                if user_prompt:
                    self.process_user_prompt(user_prompt)
            else:
                if self.wake_word.wake_word_detection():
                    self.handle_wakeword()

    def stop(self):
        self.running = False
        print("Agent stopped.")
