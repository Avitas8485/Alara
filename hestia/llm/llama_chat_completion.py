from llama_cpp import Llama
import yaml
from hestia.lib.hestia_logger import logger


llm = Llama(model_path="C:/Users/avity/Projects/models/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
            n_threads=4,
            n_threads_batch=4,
            n_ctx=2048)



# now to turn this into a function
def chat_completion(sytem_prompt: str, user_prompt: str, **kwargs):
    logger.info("Generating chat completion...")
    output = llm.create_chat_completion(
        messages=[
            {
                "role": "system",
                "content": f"{sytem_prompt}"
            },
            {
                "role": "user",
                "content": f"{user_prompt}"
            }
        ], max_tokens=1024, **kwargs
        
    )
    return output["choices"][0]["message"]["content"] # type: ignore

def load_news_prompt():
    logger.info("Loading news prompt...")
    with open("hestia/llm/prompts/prompts.yaml", "r") as file:
        prompts = yaml.load(file, Loader=yaml.FullLoader)
    return prompts["news_debrief_prompt"]

def load_weather_prompt():
    logger.info("Loading weather prompt...")
    with open("hestia/llm/prompts/prompts.yaml", "r") as file:
        prompts = yaml.load(file, Loader=yaml.FullLoader)
    return prompts["weather_report_prompt"]




