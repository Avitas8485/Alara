from llama_cpp import Llama
import yaml
from hestia.lib.hestia_logger import logger
from hestia.config.config import cfg
from hestia.lib.singleton import Singleton



    
class LlamaChatCompletion(metaclass=Singleton):
    def __init__(self):
        self.llm = self.load_llama_model()

    def load_llama_model(self, **kwargs)->Llama:
        """Load the Llama model, and unload it when done."""
        logger.info("Loading LLM...")
        llm = Llama(
            # todo: better model with the similar performance
            model_path=cfg.MIDDLE_LLAMA_MODEL_PATH,
            n_threads=cfg.LLAMA_N_THREADS,
            n_threads_batch=cfg.LLAMA_N_THREADS_BATCH,
            n_ctx=cfg.LLAMA_N_CTX,
            **kwargs)
        return llm

    def chat_completion(self, system_prompt: str, user_prompt: str, max_retries=3, grammar=None, **kwargs) -> str:
        """Generate a chat completion from the Llama model."""
        for _ in range(max_retries):
            
            logger.info("Generating chat completion...")
            output = self.llm.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": f"{system_prompt}"
                    },
                    {
                        "role": "user",
                        "content": f"{user_prompt}"
                    }
                ], max_tokens=cfg.LLAMA_MAX_TOKENS, grammar=grammar, **kwargs
            )
            logger.info("Generation complete.")
            # to prevent situations where the model outputs nothing
            if output["choices"][0]["message"]["content"] != "": # type: ignore
                return output["choices"][0]["message"]["content"] # type: ignore
            logger.warning("Model failed to generate output. Retrying...")
        logger.error("Model failed to generate output after maximum retries.")
        return "Model failed to generate output after maximum retries."
    
    
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
    llm = LlamaChatCompletion()
    print(llm.chat_completion(system_prompt, user_prompt))