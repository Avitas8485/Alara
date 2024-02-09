from llama_cpp import Llama
import yaml
# from hestia.lib.hestia_logger import logger
from contextlib import contextmanager
import logging
logger = logging.getLogger(__name__)


@contextmanager
def load_llama_model():
    """Load the Llama model, and unload it when done."""
    logger.info("Loading LLM...")
    llm = Llama(
        model_path="C:/Users/avity/Projects/models/"
                   "mistral-7b-instruct-v0.1.Q4_K_M.gguf",
        n_threads=4,
        n_threads_batch=4,
        n_ctx=2048)
    try:
        yield llm
    finally:
        logger.info("Unloading LLM...")
        llm = None


# now to turn this into a function
def chat_completion(system_prompt: str, user_prompt: str, **kwargs) -> str:
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
            ], max_tokens=2048, **kwargs
        )
    logger.info("Generation complete.")
    # to prevent situations where the model outputs nothing
    if output["choices"][0]["message"]["content"] == "": # type: ignore
        return chat_completion(system_prompt, user_prompt, **kwargs)
    return output["choices"][0]["message"]["content"] # type: ignore


def load_prompt(prompt_name: str):
    """Load a prompt from prompts.yaml."""
    logger.info(f"Loading {prompt_name} prompt...")
    with open("hestia/llm/prompts/prompts.yaml", "r") as file:
        prompts = yaml.load(file, Loader=yaml.FullLoader)
    return prompts[f"{prompt_name}"][0]


def load_prompt_txt(prompt_name: str):
    logger.info(f"Loading {prompt_name} prompt...")
    with open(f"hestia/llm/prompts/{prompt_name}.txt", "r") as file:
        return file.read()
