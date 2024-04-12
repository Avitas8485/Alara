import whisper
import os
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from typing import List
from hestia.lib.hestia_logger import logger
import logging
import threading


class StreamHandler:
    MODEL = 'small'
    ENGLISH = True
    TRANSLATE = False
    SAMPLE_RATE = 44100  # Stream device recording frequency
    BLOCK_SIZE = 110      # Block size in milliseconds
    THRESHOLD = 0.07    # Minimum volume threshold to activate listening
    VOCALS = [50, 1000]  # Frequency range to detect sounds that could be speech
    END_BLOCKS = 30      # Number of blocks to wait before sending to Whisper


    def __init__(self, assist=None, timeout=10, on_timeout=None):
        self.asst = assist if assist else {'running': True, 'talking': False, 'analyze': None}
        self.padding = 0
        self.prevblock = self.buffer = np.zeros((0,1))
        self.fileready = False
        print("\033[96mLoading Whisper Model..\033[0m", end='', flush=True)
        self.model = whisper.load_model(f'{self.MODEL}')
        print("\033[90m Done.\033[0m")
        self.timeout = timeout
        self.timer = None
        self.on_timeout = on_timeout
    def start_timer(self):
        if self.timer is not None:
            self.timer.cancel()
        self.timer = threading.Timer(self.timeout, self.stop_listening)
        self.timer.start()
        
    def stop_listening(self):
        self.asst['running'] = False
        if self.timer is not None:
            self.timer.cancel()
        self.timer = None
        print("\n\033[31mTimeout\033[0m")
        

    def callback(self, indata, frames, time, status):
        if not any(indata):
            print('\033[31m.\033[0m', end='', flush=True)
            return 
        self.process_input(indata, frames)

    def process_input(self, indata, frames):
        freq = np.argmax(np.abs(np.fft.rfft(indata[:, 0]))) * self.SAMPLE_RATE / frames
        if np.sqrt(np.mean(indata**2)) > self.THRESHOLD and self.VOCALS[0] <= freq <= self.VOCALS[1] and not self.asst['talking']:
            print('.', end='', flush=True)
            self.buffer = self.prevblock.copy() if self.padding < 1 else np.concatenate((self.buffer, indata))
            self.padding = self.END_BLOCKS
            if self.timer is not None:
                self.timer.cancel()
                self.timer = None
        else:
            self.process_silence(indata)

    def process_silence(self, indata):
        self.padding -= 1
        if self.padding > 1:
            self.buffer = np.concatenate((self.buffer, indata))
        elif self.padding < 1 < self.buffer.shape[0] > self.SAMPLE_RATE:
            self.fileready = True
            write('dictate.wav', self.SAMPLE_RATE, self.buffer)
            self.buffer = np.zeros((0,1))
        elif self.padding < 1 < self.buffer.shape[0] < self.SAMPLE_RATE:
            self.buffer = np.zeros((0,1))
            print("\033[2K\033[0G", end='', flush=True)
        else:
            self.prevblock = indata.copy()

    
    def listen(self)-> str|None:
        print("\033[32mListening.. \033[37m(Ctrl+C to Quit)\033[0m")
        self.asst['running'] = True
        with sd.InputStream(channels=1, callback=self.callback, blocksize=int(self.SAMPLE_RATE * self.BLOCK_SIZE / 1000), samplerate=self.SAMPLE_RATE):
            print("getting input stream")
            if self.timer is None:
                print("Starting timer")
                self.start_timer()
            while self.asst['running']: 
                if self.fileready:
                    print("\n\033[90mTranscribing..\033[0m")
                    result = self.model.transcribe('dictate.wav',fp16=False,language='en' if self.ENGLISH else '',task='translate' if self.TRANSLATE else 'transcribe')
                    print(f"\033[1A\033[2K\033[0G{result['text']}")
                    transcription = result['text']
                    if self.asst['analyze']: self.asst['analyze'](result['text'])
                    self.fileready = False
                    os.remove('dictate.wav')
                    if isinstance(transcription, list):
                        transcription = ' '.join(transcription)
                    return transcription
        return None
                


        
if __name__ == "__main__":
    stream_handler = StreamHandler()
    while True:
        
        stream_handler.listen()
        print("Done")