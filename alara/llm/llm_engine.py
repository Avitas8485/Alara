from alara.llm.llama_chat_completion import LlamaChatCompletion
from alara.llm.llama_cpp_server import LlmServer
from alara.lib.singleton import Singleton
from alara.lib.logger import logger
from enum import Enum

class LlmType(Enum):
    llama_server = 'llama_server'
    llama_cpp = 'llama_cpp'

class LlmEngine(metaclass=Singleton):
    @staticmethod
    def load_llm(llm_type: LlmType=LlmType.llama_cpp):
        if llm_type == LlmType.llama_server:
            return LlmServer()
        elif llm_type == LlmType.llama_cpp:
            return LlamaChatCompletion()
        else:
            raise ValueError('Invalid LLM type')
        

