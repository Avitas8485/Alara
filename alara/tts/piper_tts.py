import subprocess
import re
from .base_tts import BaseTTS
from alara.config.config import cfg
from alara.tools.text_parser.format_en import Converter
from alara.lib.logger import logger
import sounddevice as sd
import numpy as np

class PiperTTSError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
    
    
        
    

class PiperTTS(BaseTTS):
    def __init__(self) -> None:
        self.model_path = cfg.PIPER_TTS_MODEL_PATH
        self.piper_path = cfg.PIPER_TTS_EXE_PATH
        self.output_file = f"alara/tts/outputs/temp.wav"
        self.params = {
            "active": True,
            "autoplay": True,
            "show_text": True,
            "ignore_asterisk_text": True,
            "quiet": False,
            "selected_model": "",
            "noise_scale": 0.66,
            "length_scale": 1,
            "noise_w": 0.8,
            "sentence_silence": 0.1,
        }
        logger.info("Piper TTS initialized.")
        
    def clean_text(self, text: str):
        converter = Converter()
        cleaned_text = text
        
        replacements = {
            '&#x27;': "'",
            '&quot;': '"',
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&nbsp;': ' ',
            '&copy;': '©',
            '&reg;': '®'
        }

        for key, value in replacements.items():
            cleaned_text = cleaned_text.replace(key, value)
            
        cleaned_text = cleaned_text.replace("***", "*").replace("**", "*")
        cleaned_text = re.sub(r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]+", "", cleaned_text)
        
        # Remove any non-ascii characters
        cleaned_text = cleaned_text.encode('ascii', 'ignore').decode('ascii')
        cleaned_text = converter.convert_in_text(cleaned_text)
        return cleaned_text
    
    def synthesize(self, text: str):
        cleaned_text = self.clean_text(text)
        process = subprocess.Popen(
            [
                self.piper_path,
                '--model', self.model_path,
                '--output_file', self.output_file,
                '--sentence_silence', str(self.params['sentence_silence']),
                '--noise_scale', str(self.params['noise_scale']),
                '--length_scale', str(self.params['length_scale']),
                '--noise_w', str(self.params['noise_w']),
                '--output-raw'
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=False,
        )
        
        if process.stdin is None or process.stdout is None:
            raise PiperTTSError("Failed to create subprocess")
        
        
        stream = sd.OutputStream(samplerate=22050, channels=1, dtype=np.int16)
        stream.start()
        process.stdin.write(cleaned_text.encode())
        process.stdin.close()
        data = process.stdout.read(1024)
        while len(data) > 0:
            data = np.frombuffer(data, dtype=np.int16)
            stream.write(data)
            data = process.stdout.read(1024)
        stream.stop()
        stream.close()
        process.wait()
        
    
    def synthesize_to_file(self, output_dir: str='alara/tts/outputs', output_filename: str='output', text: str=''):
        cleaned_text = self.clean_text(text)
        process = subprocess.Popen(
            [
                self.piper_path,
                '--model', self.model_path,
                '--output_file', f"{output_dir}\\{output_filename}.wav",
                '--sentence_silence', str(self.params['sentence_silence']),
                '--noise_scale', str(self.params['noise_scale']),
                '--length_scale', str(self.params['length_scale']),
                '--noise_w', str(self.params['noise_w']),
            ],
            stdin=subprocess.PIPE,
            text=True,
        )
        
        process.communicate(cleaned_text)
        
        process.wait()
        
        return self.output_file
    
    