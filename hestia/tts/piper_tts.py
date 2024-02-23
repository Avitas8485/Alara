import subprocess

import re
from hestia.tts.base_tts import BaseTTS

class PiperTTSError(Exception):
    pass

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
            "sentence_silence": 0.2
        }
        
    def clean_text(self, text):
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
        
        # Ignore text between asterisks if option is enabled
        
        return cleaned_text
    
    def synthesize(self, text):
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
        
    def synthesize_to_file(self, text):
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
    text = """Dynamic Adjustments to Thread Priorities:
   - Example: In a gaming application, different threads handle tasks like physics calculations, rendering, and input processing. Replicating scheduling information in TCBs allows for dynamic adjustments to thread priorities. For instance, when a user initiates a resource-intensive action, like a complex in-game simulation, the priority of the corresponding thread can be temporarily increased to ensure a smoother user experience.
    - Example: In a real-time operating system, a thread that handles sensor data may need to be given a higher priority when the system is in a critical state, such as when a vehicle is approaching an obstacle. This ensures that the sensor data is processed quickly and accurately, allowing the system to respond appropriately.
    - Example: In a web server, threads that handle incoming requests can have their priorities adjusted based on the current load on the server. When the server is under heavy load, threads handling critical requests can be given higher priority to ensure timely responses."""
    piper = PiperTTS()
    piper.synthesize(text)
    piper.synthesize_to_file(text)
 

if __name__ == "__main__":
    main()