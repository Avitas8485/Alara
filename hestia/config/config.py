from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    def __init__(self):
        self.OPEN_WEATHER_API_KEY = os.getenv('OPEN_WEATHER_API_KEY')
        self.VISUAL_CROSSING_API_KEY = os.getenv('VISUAL_CROSSING_API_KEY')
        self.NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
        self.WAQI_API_KEY = os.getenv('WAQI_API_KEY')
        self.NASA_API_KEY = os.getenv('NASA_API_KEY')
        
        self.DB_URL = os.getenv('DB_URL')
        self.THREAD_POOL_SIZE = int(os.getenv('THREAD_POOL_SIZE', 10))
        self.PROCESS_POOL_SIZE = int(os.getenv('PROCESS_POOL_SIZE', 5))
        
        self.LLAMA_MODEL_PATH = os.getenv('LLAMA_MODEL_PATH', '')
        self.LLAMA_N_THREADS = int(os.getenv('LLAMA_N_THREADS', 4))
        self.LLAMA_N_THREADS_BATCH = int(os.getenv('LLAMA_N_THREADS_BATCH', 4))
        self.LLAMA_N_CTX = int(os.getenv('LLAMA_N_CTX', 2048))
        self.LLAMA_MAX_TOKENS = int(os.getenv('LLAMA_MAX_TOKENS', 2048))
        
        self.REPORT_SUMMARY_PATH = os.getenv('REPORT_SUMMARY_PATH', 'hestia/tools/reports/summary')
        self.TTS_PATH = os.getenv('TTS_PATH')
        self.PROMPT_PATH = os.getenv('PROMPT_PATH')
        self.SCHEDULE_PATH = os.getenv('SCHEDULE_PATH')

        self.XTTS_OUTPUT_PATH = os.getenv('XTTS_OUTPUT_PATH', 'hestia/text_to_speech/output')
        self.XTTS_CONFIG_PATH = os.getenv('XTTS_CONFIG_PATH','')
        self.XTTS_VOCAB_PATH = os.getenv('XTTS_VOCAB_PATH', '') 
        self.XTTS_SPEAKER_PATH = os.getenv('XTTS_SPEAKER_PATH', '')
        self.XTTS_MODEL_DIR = os.getenv('XTTS_MODEL_DIR', '')
        
cfg = Config()

