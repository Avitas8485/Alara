from alara.stt.whisper_stt import StreamHandler
from alara.stt.wakeword import WakeWord
from alara.nlp.intent_recognition import IntentRecognition
from alara.lib.singleton import Singleton
from alara.tts.tts_engine import TTSEngine
from alara.llm.llm_engine import LlmEngine
from alara.automation.automation_handler import AutomationHandler
from alara.skills.skill_manager import SkillManager
from alara.automation.event import Event, State
from alara.lib.logger import Logger
from alara.llm.grammar.pydantic_models_to_grammar import generate_gbnf_grammar_and_documentation, \
    create_dynamic_model_from_function
import json
import time





class Agent(metaclass=Singleton):

    def __init__(self):
        self.tts = TTSEngine.load_tts()
        self.skill_manager = SkillManager()
        self.automation_handler = AutomationHandler(skill_manager=self.skill_manager)
        self.stream_handler = StreamHandler()
        self.wake_word = WakeWord()
        self.intent_recognition = IntentRecognition(skill_manager=self.skill_manager)
        self.system_prompt = "Your name is Alara. You are an AI assistant that helps people with their daily tasks."
        self.llm = LlmEngine.load_llm()
        self.running = True
        
        self.last_interaction = None
        self.agent_name = "Alara"
        self.agent_state = None
        self.logger = Logger("Alara").logger
        self.agent_state = self.automation_handler.state_machine.add_state(
            State(entity_id=self.agent_name, state="idle", attributes={"last_interaction": None}))
    
    def process_user_prompt(self, user_prompt):
        self.logger.debug(f"User prompt: {user_prompt}")
        self.automation_handler.state_machine.set_state(entity_id=self.agent_name, new_state="processing",
                                                        attributes={"last_interaction": self.last_interaction})
        intent = self.intent_recognition.get_intent(user_prompt)
        try:
            skill = self.automation_handler.skill_manager.load_skill(intent)
            features = skill.get_features()
            models = [create_dynamic_model_from_function(getattr(skill, feature)) for feature in features]
            gbnf, documentation = generate_gbnf_grammar_and_documentation(
                pydantic_model_list=models, outer_object_name="function",
                outer_object_content="params", model_prefix="Function", fields_prefix="Parameters"
            )
            system_prompt = f"""You are an advanced AI assistant tasked with generating JSON objects. These objects represent function calls that you can make to fulfill the user's request. Given a prompt, extract the relevant information and call a function. Should the prompt not contain enough information to call a function, use the default values. Below is a list of your available function calls, only one function can be called at a time so choose wisely:\n\n{documentation}"""
            output = self.llm.chat_completion(system_prompt=system_prompt, user_prompt=user_prompt, grammar=gbnf)
            params = json.loads(output)
            function = getattr(skill, params['function'])
            return function(**params['params'])
        except Exception as e:
            self.logger.error(f"Error calling skill: {e}")
            output = self.llm.chat_completion(system_prompt=self.system_prompt,
                                              user_prompt=f"Notify the user that the feature {function} has not"
                                                          f"been implemented yet.")
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
