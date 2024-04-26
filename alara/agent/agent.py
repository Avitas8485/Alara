from alara.stt.whisper_stt import StreamHandler
from alara.stt.wakeword import WakeWord
from alara.nlp.intent_recognition import IntentRecognition
from alara.lib.singleton import Singleton
from alara.tts.piper_tts import PiperTTS
from alara.llm.llm_engine import LlmEngine
from alara.automation.automation_handler import AutomationHandler
from alara.automation.event import Event, State
from alara.lib.logger import Logger
from alara.llm.grammar.pydantic_models_to_grammar import generate_gbnf_grammar_and_documentation, \
    create_dynamic_model_from_function
import json
from llama_cpp.llama_grammar import LlamaGrammar
import time
from typing import Callable
import inspect


def create_grammar(function: Callable):
    model = create_dynamic_model_from_function(function)
    tool = [model]
    gbnf, documentation = generate_gbnf_grammar_and_documentation(
        pydantic_model_list=tool, outer_object_name="function",
        outer_object_content="params", model_prefix="Function", fields_prefix="Parameters"
    )
    return gbnf, documentation


class Agent(metaclass=Singleton):

    def __init__(self):

        self.tts = PiperTTS()
        self.stream_handler = StreamHandler()
        self.wake_word = WakeWord()
        self.intent_recognition = IntentRecognition()
        self.system_prompt = "Your name is Alara. You are an AI assistant that helps people with their daily tasks."
        self.llm = LlmEngine.load_llm()
        self.running = True
        self.automation_handler = AutomationHandler()
        self.last_interaction = None
        self.agent_name = "Alara"
        self.agent_state = None
        self.logger = Logger("Alara").logger
        self.agent_state = self.automation_handler.state_machine.add_state(
            State(entity_id=self.agent_name, state="idle", attributes={"last_interaction": None}))

    def on_timeout(self):
        self.tts.synthesize("I'm sorry, I didn't catch that. Please try again.")
        # reset the last interaction time so that the agent can require the wake word to be detected
        self.last_interaction = None

    def param_feature_call(self, function: Callable, user_prompt: str):
        gbnf, documentation = create_grammar(function)
        system_prompt = f"""You are an advanced AI assistant. You are interacting with the user and with your 
        environment by calling functions. You can call functions by writing JSON objects, which represents specific 
        function calls. Given a prompt, extract the relevant information and call the function. Only use the 
        information that is given in the prompt. Do not use any external information. If the prompt does not contain 
        enough information to call a function, use the default values. {documentation}"""

        output = self.llm.chat_completion(system_prompt=system_prompt, user_prompt=user_prompt, grammar=gbnf)
        params = json.loads(output)
        return function(**params['params'])

    def process_user_prompt(self, user_prompt):
        self.logger.debug(f"User prompt: {user_prompt}")
        self.automation_handler.state_machine.set_state(entity_id=self.agent_name, new_state="processing",
                                                        attributes={"last_interaction": self.last_interaction})
        intent, sub_intent = self.intent_recognition.get_intent(user_prompt)
        self.logger.debug(f"Intent: {intent}, Sub-intent: {sub_intent}")
        try:
            skill = self.automation_handler.skill_manager.load_skill(intent)
            #skill = self.skill_manager.load_skill(intent)
            feature = skill.load_feature(sub_intent)
            if hasattr(feature, "requires_prompt"):
                self.logger.debug("Feature requires prompt.")
                self.automation_handler.skill_manager.call_feature(sub_intent, user_prompt)
                #self.skill_manager.call_feature(sub_intent, user_prompt)

            feature_args = inspect.getfullargspec(feature).args  # check if the feature has arguments
            # remove the self argument
            feature_args = [arg for arg in feature_args if arg != "self"]
            if not feature_args:
                self.automation_handler.skill_manager.call_feature(sub_intent)
                #self.skill_manager.call_feature(sub_intent)
            else:
                self.param_feature_call(feature, user_prompt)
        except Exception as e:
            self.logger.error(f"Error calling skill: {e}")
            output = self.llm.chat_completion(system_prompt=self.system_prompt,
                                              user_prompt=f"Notify the user that the feature {sub_intent} has not "
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
