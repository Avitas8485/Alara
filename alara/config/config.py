from dotenv import load_dotenv
import os

load_dotenv('.env')

class Config:
    """Config class to store all the environment variables."""
    def __init__(self):
        self.OPEN_WEATHER_API_KEY = os.getenv('OPEN_WEATHER_API_KEY')
        self.VISUAL_CROSSING_API_KEY = os.getenv('VISUAL_CROSSING_API_KEY')
        self.NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
        self.WAQI_API_KEY = os.getenv('WAQI_API_KEY')
        self.NASA_API_KEY = os.getenv('NASA_API_KEY')
        
        self.SMART_LLAMA_MODEL_PATH = os.getenv('SMART_LLAMA_MODEL_PATH', '')
        self.FAST_LLAMA_MODEL_PATH = os.getenv('FAST_LLAMA_MODEL_PATH', '')
        self.MIDDLE_LLAMA_MODEL_PATH = os.getenv('MIDDLE_LLAMA_MODEL_PATH', '')
        self.LLAMA_MODEL_PATH = os.getenv('LLAMA_MODEL_PATH', '')
        
        self.LLMSERVER_URL = os.getenv('LLMSERVER_URL', '')
        
        self.LLAMA_N_THREADS = int(os.getenv('LLAMA_N_THREADS', ''))
        self.LLAMA_N_THREADS_BATCH = int(os.getenv('LLAMA_N_THREADS_BATCH', ''))
        self.LLAMA_N_CTX = int(os.getenv('LLAMA_N_CTX', ''))
        self.LLAMA_MAX_TOKENS = int(os.getenv('LLAMA_MAX_TOKENS', ''))
        
        self.PIPER_TTS_MODEL_PATH = os.getenv('PIPER_TTS_MODEL_PATH', '')
        self.PIPER_TTS_EXE_PATH = os.getenv('PIPER_TTS_EXE_PATH', '')
        
        self.XTTS_OUTPUT_PATH = os.getenv('XTTS_OUTPUT_PATH', '')
        self.XTTS_CONFIG_PATH = os.getenv('XTTS_CONFIG_PATH','')
        self.XTTS_VOCAB_PATH = os.getenv('XTTS_VOCAB_PATH', '') 
        self.XTTS_SPEAKER_PATH = os.getenv('XTTS_SPEAKER_PATH', '')
        self.XTTS_MODEL_DIR = os.getenv('XTTS_MODEL_DIR', '')
        
        self.PROMPT_PATH = os.getenv('PROMPT_PATH', '')

cfg = Config()

