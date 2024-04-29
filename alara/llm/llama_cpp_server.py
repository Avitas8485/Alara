import requests
from requests.exceptions import ConnectionError
from alara.lib.logger import logger
from alara.lib.singleton import Singleton


class LlmServer(metaclass=Singleton):
    def __init__(self, url: str='http://localhost:8080/v1/chat/completions'):
        self.url = url
        logger.info("Using Llama server, ensure that the server is running and supports Llama Grammar.")
    
    def chat_completion(self, system_prompt: str, user_prompt: str, max_retries: int=3, grammar:str|None=None):
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
                    'max_tokens': 3072,
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
    