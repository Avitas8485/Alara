import subprocess

import re
from .base_tts import BaseTTS
from ..tools.text_parser.format_en import Converter

class PiperTTSError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
    
    
        
    

class PiperTTS(BaseTTS):
    def __init__(self) -> None:
        self.model_path = 'hestia\\piper\\models\\en_US-hestia-large-high.onnx'
        self.output_file = f"hestia\\tts\\outputs\\temp.wav"
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
                "hestia\\piper\\piper.exe",
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
        
        import pyaudio
        chunk = 1024
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=22050,
                        output=True)
        process.stdin.write(cleaned_text.encode())
        process.stdin.close()
        data = process.stdout.read(chunk)
        while len(data) > 0:
            stream.write(data)
            data = process.stdout.read(chunk)
        stream.close()
        process.wait()
        p.terminate()
        
    def synthesize_to_file(self, text: str):
        cleaned_text = self.clean_text(text)
        process = subprocess.Popen(
            [
                "hestia\\piper\\piper.exe",
                '--model', self.model_path,
                '--output_file', self.output_file,
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
    

def main():
    text = """It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout.
    The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English.
    Many desktop publishing packages and web page editors now use Lorem Ipsum as their default model text, and a search for 'lorem ipsum' will uncover many web sites still in their infancy.
    Various versions have evolved over the years, sometimes by accident, sometimes on purpose (injected humour and the like).
    
    It is 9:00 AM. Today is 02/23/2004 and the weather is 72 degrees Fahrenheit."""
    piper = PiperTTS()
    piper.synthesize(text)
    piper.synthesize_to_file(text)
 

if __name__ == "__main__":
    main()