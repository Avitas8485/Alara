from llama_cpp import Llama
import yaml
#from hestia.lib.hestia_logger import logger
from contextlib import contextmanager
import logging
logger = logging.getLogger(__name__)

@contextmanager
def load_llama_model():
    """Load the Llama model, and unload it when done."""
    logger.info("Loading LLM...")
    llm =  Llama(model_path="C:/Users/avity/Projects/models/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
            n_threads=2,
            n_threads_batch=2,
            n_ctx=2048)
    try:
        yield llm
    finally:
        logger.info("Unloading LLM...")
        llm = None




# now to turn this into a function
def chat_completion(system_prompt: str, user_prompt: str, **kwargs)->str:
    """Generate a chat completion from the Llama model."""
    logger.info("Generating chat completion...")
    with load_llama_model() as llm:
        output = llm.create_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": f"{system_prompt}"
                },
                {
                    "role": "user",
                    "content": f"{user_prompt}"
                }
            ], max_tokens=1024, **kwargs
        )
    logger.info("Generation complete.")
    return output["choices"][0]["message"]["content"] # type: ignore


def load_news_prompt():
    """Load the news prompt from prompts.yaml."""
    logger.info("Loading news prompt...")
    with open("hestia/llm/prompts/prompts.yaml", "r") as file:
        prompts = yaml.load(file, Loader=yaml.FullLoader)
    return prompts["news_debrief_prompt"]

def load_weather_prompt():
    """Load the weather prompt from prompts.yaml."""
    logger.info("Loading weather prompt...")
    with open("hestia/llm/prompts/prompts.yaml", "r") as file:
        prompts = yaml.load(file, Loader=yaml.FullLoader)
    return prompts["weather_report_prompt"]

def load_schedule_prompt():
    """Load the schedule prompt from prompts.yaml."""
    logger.info("Loading schedule prompt...")
    with open("hestia/llm/prompts/prompts.yaml", "r") as file:
        prompts = yaml.load(file, Loader=yaml.FullLoader)
    return prompts["schedule_report_prompt"]





