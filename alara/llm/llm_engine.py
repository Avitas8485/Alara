from alara.llm.llama_chat_completion import LlamaChatCompletion
from alara.llm.llama_cpp_server import LlmServer
from enum import Enum

class LlmType(Enum):
    llama_server = 'llama_server'
    llama_cpp = 'llama_cpp'

class LlmEngine:
    @staticmethod
    def load_llm(llm_type: LlmType=LlmType.llama_server):
        if llm_type == LlmType.llama_server:
            return LlmServer()
        elif llm_type == LlmType.llama_cpp:
            return LlamaChatCompletion()
        else:
            raise ValueError('Invalid LLM type')
        

