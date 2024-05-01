from llama_cpp import Llama
from llama_cpp.llama_grammar import LlamaGrammar
import yaml
from alara.lib.logger import logger
from alara.config.config import cfg
from alara.lib.singleton import Singleton


class LlamaChatCompletion(metaclass=Singleton):
    """A wrapper around llama_cpp for generating chat completions.
    Attributes:
        llm: Llama: The Llama model."""
    
    def __init__(self):
        self.llm = self.load_llama_model()

    def load_llama_model(self, **kwargs) -> Llama:
        """Load the Llama model, and unload it when done.
        Args:
            kwargs: dict: Additional keyword arguments to pass to the model."""
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
        
        """Generate a chat completion from the LLM
        Args:
            system_prompt: str: The system prompt.
            user_prompt: str: The user prompt.
            max_retries: int: The maximum number of retries to generate a completion.
            grammar: str or LlamaGrammar: The grammar to use for the completion.
            kwargs: dict: Additional keyword arguments to pass to the model.
        Returns:
            str: The generated chat completion."""
        if grammar:
            if isinstance(grammar, str):
                grammar = LlamaGrammar.from_string(grammar)       
            elif isinstance(grammar, LlamaGrammar):
                pass
            else:
                raise ValueError("Invalid grammar type. Currently only str and LlamaGrammar are supported.")
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
            if output["choices"][0]["message"]["content"] != "":  # type: ignore
                return output["choices"][0]["message"]["content"]  # type: ignore
            logger.warning("Model failed to generate output. Retrying...")
        logger.error("Model failed to generate output after maximum retries.")
        return "Model failed to generate output after maximum retries."


def load_prompt(prompt_name: str):
    """Load a prompt from prompts.yaml.
    Args:
        prompt_name: str: The name of the prompt."""
    logger.info(f"Loading {prompt_name} prompt...")
    with open("alara/llm/prompts/prompts.yaml", "r") as file:
        prompts = yaml.load(file, Loader=yaml.FullLoader)
    return prompts[f"{prompt_name}"][0]

def load_prompt_txt(prompt_name: str):
    """Load a prompt from a text file.
    Args:
        prompt_name: str: The name of the prompt."""
    logger.info(f"Loading {prompt_name} prompt...")
    with open(f"alara/llm/prompts/{prompt_name}.txt", "r") as file:
        return file.read()