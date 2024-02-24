from llama_cpp import Llama
import yaml
# from hestia.lib.hestia_logger import logger
import logging
logger = logging.getLogger(__name__)
from hestia.config.config import cfg


def load_llama_model()->Llama:
    """Load the Llama model, and unload it when done."""
    logger.info("Loading LLM...")
    llm = Llama(
        model_path=cfg.MIDDLE_LLAMA_MODEL_PATH,
        n_threads=cfg.LLAMA_N_THREADS,
        n_threads_batch=cfg.LLAMA_N_THREADS_BATCH,
        n_ctx=cfg.LLAMA_N_CTX, chat_format="chatml")
    return llm

def chat_completion(system_prompt: str, user_prompt: str, **kwargs) -> str:
    """Generate a chat completion from the Llama model."""
    logger.info("Generating chat completion...")
    llm = load_llama_model()
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
        ], max_tokens=cfg.LLAMA_MAX_TOKENS, **kwargs
    )
    logger.info("Generation complete.")
    # to prevent situations where the model outputs nothing
    if output["choices"][0]["message"]["content"] == "": # type: ignore
        print("Model output was empty. Retrying...")
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


if __name__ == "__main__":
    system_prompt = "You are an AI assistant that helps people with their daily tasks."
    user_prompt = "What is your name?"
    print(chat_completion(system_prompt, user_prompt))