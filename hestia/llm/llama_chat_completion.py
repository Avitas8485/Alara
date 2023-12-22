from llama_cpp import Llama
import yaml


llm = Llama(model_path="C:/Users/avity/Projects/models/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
            n_threads=4,
            n_threads_batch=4,
            n_ctx=2048)



# now to turn this into a function
def chat_completion(sytem_prompt: str, user_prompt: str):
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
        ], max_tokens=1024
        
    )
    return output

def load_news_prompt():
    with open("hestia/llm/prompts/prompts.yaml", "r") as file:
        prompts = yaml.load(file, Loader=yaml.FullLoader)
    return prompts["news_debrief_prompt"]

def load_weather_prompt():
    with open("hestia/llm/prompts/prompts.yaml", "r") as file:
        prompts = yaml.load(file, Loader=yaml.FullLoader)
    return prompts["weather_report_prompt"]




if __name__ == '__main__':
    weather = """Weather report for Buford:
                Address: Buford
                Description: Cooling down with a chance of rain Monday & Tuesday.
                Day: 2023-12-22
                Max Temperature: 56.9
                Min Temperature: 36.7
                Current Temperature: 56.5
                Humidity: 50.1
                Pressure: 1027.8
                Wind Speed: 4.7
                Wind Gust: 8.1
                Sunrise Time: 07:38:23
                Sunset Time: 17:30:53
                Conditions: Clear
                Conditions Description: clear-day"""
    print(chat_completion(sytem_prompt=load_weather_prompt(), user_prompt=weather))