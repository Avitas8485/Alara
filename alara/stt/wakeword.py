
# Imports
import pyaudio
import numpy as np
import openwakeword.utils as utils
from openwakeword.model import Model
import logging
from rich import print
from alara.lib.hestia_logger import logger

class WakeWord:
    def __init__(self, model_path="hestia/stt/Alara.onnx", inference_framework="onnx", chunk_size=1280):
        self.chunk_size = chunk_size
        self.model = self.load_model(model_path, inference_framework)
        self.mic_stream = self.get_mic_stream()

    def load_model(self, model_path, inference_framework="onnx"):
        logger.info(f"Loading wakeword model from {model_path}")
        try:
            owwModel = Model(wakeword_models=[model_path], inference_framework=inference_framework)
        except Exception as e:
            utils.download_models()
            owwModel = Model(wakeword_models=[model_path], inference_framework=inference_framework)
        return owwModel
    
    def get_mic_stream(self):
        logger.info("Initializing microphone stream")
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        audio = pyaudio.PyAudio()
        mic_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=self.chunk_size)
        return mic_stream
    
    def predict_wakeword(self):
        audio = np.frombuffer(self.mic_stream.read(self.chunk_size), dtype=np.int16)
        return self.model.predict(audio)
    
    def print_wakeword_status(self):
        while True:
            prediction = self.predict_wakeword()
            # Column titles
            n_spaces = 16
            output_string_header = """
                Model Name         | Score | Wakeword Status
                --------------------------------------
                """
            
            for mdl in self.model.prediction_buffer.keys():
                # Add scores in formatted table
                scores = list(self.model.prediction_buffer[mdl])
                curr_score = format(scores[-1], '.20f').replace("-", "")

                output_string_header += f"""{mdl}{" "*(n_spaces - len(mdl))}   | {curr_score[0:5]} | {"--"+" "*20 if scores[-1] <= 0.5 else "Wakeword Detected!"}
                """ 
            # Print results table
            
            print("\033[F"*(4*len(self.model.prediction_buffer.keys())+1))
            print(output_string_header, "                             ", end='\r')
            
    def wake_word_detection(self):
        logger.info("Listening for wakeword..")
        print("Say 'Alara' to initiate voice assistant..")
        while True:
            self.predict_wakeword()
            for mdl in self.model.prediction_buffer.keys():
                scores = list(self.model.prediction_buffer[mdl])
                if scores[-1] > 0.5:
                    print(f"Wakeword detected! '{mdl}' with score {scores[-1]}")
                    logger.info(f"Wakeword detected! '{mdl}' with score {scores[-1]}")
                    return True
                
    def clear_wakeword_buffer(self):
        """Clears the prediction buffer of the wakeword model.
        It is important to clear the buffer after a wakeword has been detected to avoid
        the wakeword being detected multiple times in a row."""
        while self.model.prediction_buffer:
            self.model.prediction_buffer.popitem()
            
        
    def run(self):
        if self.wake_word_detection():
            print("Wakeword detected!, initiating voice assistant..")
            logger.info("Wakeword detected!, initiating voice assistant..")
            
            

if __name__ == "__main__":
    wakeword = WakeWord()
    wakeword.run()