import requests
from requests.exceptions import ConnectionError
from alara.lib.logger import logger
from alara.lib.singleton import Singleton
from alara.config.config import cfg

class LlmServer(metaclass=Singleton):
    """A class to interact with LLM servers. To use this class, ensure that the server is running and supports Llama Grammar.
    Attributes:
        url: str: The URL of the LLM server. Uses the default URL from the .env file if not provided."""
    def __init__(self, url: str=cfg.LLMSERVER_URL):
        self.url = url
        logger.info("Using Llama server, ensure that the server is running and supports Llama Grammar.")
    
    def chat_completion(self, system_prompt: str, user_prompt: str, max_retries: int=3, grammar:str|None=None):
        """Generate a chat completion from the LLM server.
        Args:
            system_prompt: str: The system prompt.
            user_prompt: str: The user prompt.
            max_retries: int: The maximum number of retries to generate a completion.
            grammar: str: The grammar to use for the completion.
        Returns:
            str: The generated chat completion."""
        for _ in range(max_retries):
            try:
                logger.info("Generating chat completion...")
                data = {
                    'messages': [
                        {
                            'role': 'system',
                            'content': system_prompt
                        },
                        {
                            'role': 'user',
                            'content': user_prompt
                        }
                    ],
                    'max_tokens': cfg.LLAMA_MAX_TOKENS,
                    'grammar': grammar
                }
                response = requests.post(self.url, json=data)
                if response.status_code == 200:
                    response_json = response.json()
                    return response_json['choices'][0]['message']['content']
                else:
                    logger.warning("Model failed to generate output. Retrying...")
            except ConnectionError:
                logger.error("Failed to generate completion")
        logger.error("Model failed to generate output after maximum retries.")
        return "Model failed to generate output after maximum retries."
    