import pyaudio
import wave
from typing import List
import textwrap

def play_audio(audio_path):
        """Play the audio."""   
        chunk = 1024
        try:
            with wave.open(audio_path, 'rb') as wf:
                p = pyaudio.PyAudio()
                stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                                channels=wf.getnchannels(),
                                rate=wf.getframerate(),
                                output=True)
                data = wf.readframes(chunk)
                while len(data) > 0:
                    stream.write(data)
                    data = wf.readframes(chunk)
                stream.close()
        except Exception as e:
            print(f"Error: {e}")
    
