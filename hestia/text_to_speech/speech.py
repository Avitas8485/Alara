# Description: This file contains the code for the TextToSpeechSystem class.
import os
from pydub import AudioSegment
import wave
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import soundfile as sf
from hestia.lib.hestia_logger import logger
from typing import List


class TextToSpeechSystem:
    """This class contains the code for the TextToSpeechSystem.
    Attributes:
        config: The configuration for the TextToSpeechSystem.
        vocab_path: The path to the vocabulary file.
        speaker_path: The path to the speaker file.
        model_dir: The path to the model directory.
        model: The model to use for the TextToSpeechSystem."""
    def __init__(self):
        self.config = XttsConfig()
        self.config.load_json("C:/Users/avity/Projects/models/tts/xtts_v2-001/config.json")
        self.vocab_path = "C:/Users/avity/Projects/models/tts/xtts_v2-001/vocab.json"
        self.speaker_path = "hestia/text_to_speech/voice_samples/output_00000017.wav"
        self.model_dir = "C:/Users/avity/Projects/models/tts/xtts_v2-001/"
        self.model = None
        logger.info("TextToSpeechSystem initialized.")
        
    def split_into_sentences_using_nlp(self, text)->List[str]:
        """Split the text into sentences using NLP.
        Args:
            text: The text to split into sentences.
        Returns:
            List[str]: The sentences."""
        logger.info("Processing text...")
        import nltk
        nltk.download('punkt', quiet=True)
        from nltk.tokenize import sent_tokenize
        sentences = sent_tokenize(text)
        import re
        # in case the sentence tokenizer splits a number into two sentences.
        merged_sentences = []
        i = 0
        while i < len(sentences):
            if re.search(r'\d\.$', sentences[i]):
                merged_sentences.append(sentences[i] + ' ' + sentences[i+1])
                i += 2
            else:
                merged_sentences.append(sentences[i])
                i += 1
        logger.info("Text processed.")
                
        return merged_sentences
    
    def load_txt_from_file(self,file_path)->str:
        """Load text from a file.
        Args:
            file_path: The path to the file.
        Returns:
            str: The text from the file."""
        with open(file_path, "r") as file:
            text = file.read()
        return text
    
    
    def convert_sentences_to_wav_files(self,filename: str, output_dir: str, sentences: list)->List[str]:
        """Convert the sentences to wav files.
        Args:
            filename(str): The name of the file.
            output_dir(str): The directory to output the wav files to.
            sentences(list): The sentences to convert to wav files.
        Returns:
            List[str]: The paths to the wav files."""
        logger.info("Converting sentences to wav files...")
        self.model = Xtts.init_from_config(self.config)
        logger.info("Loading TTS model...")
        self.model.load_checkpoint(config=self.config, checkpoint_dir=self.model_dir, vocab_path=self.vocab_path)
        soundbite_filepaths = []
        for i, sentence in enumerate(sentences):
            soundbite_filepath = f"{output_dir}/{filename}_{i}.wav"
            gpt_cond_latent, speaker_embedding = self.model.get_conditioning_latents(audio_path=[self.speaker_path])
            out = self.model.inference(
                text=sentence,
                gpt_cond_latent=gpt_cond_latent,
                speaker_embedding=speaker_embedding,
                language="en",
            )
            sf.write(soundbite_filepath, out["wav"], 24000)
            soundbite_filepaths.append(soundbite_filepath)
        logger.info("Unloading TTS model...")
        self.model = None
        logger.info("Sentences converted to wav files.")
        return soundbite_filepaths
    
    def merge_wav_files_into_one(self,format: str,output_dir:str,output_filename:str,soundbite_filepaths:list):
        """Merge the wav files into one.
        Args:
            format(str): The format to merge the wav files into.
            output_dir(str): The directory to output the merged wav file to.
            output_filename(str): The name of the merged wav file.
            soundbite_filepaths(list): The paths to the wav files to merge."""
        logger.info("Processing wav files...")
        if format not in ["mp3","wav"]:
            raise Exception(f"Format:{format} not supported.")
        output_filepath=f"{output_dir}/{output_filename}.{format}"
        print(f"output_filepath={output_filepath}")
        combined_sounds = None
        for soundbite_filepath in soundbite_filepaths:
            print(f'soundbite_filepath={soundbite_filepath}')
            some_sound=AudioSegment.from_wav(soundbite_filepath)
            if combined_sounds is None:
                combined_sounds=some_sound    
            else:
                combined_sounds=combined_sounds+some_sound

        combined_sounds.export(output_filepath, format=format) #type: ignore

    def get_output_files(self,output_dir,soundbite_filename)->List[str]:
        """Get the output files.
        Args:
            output_dir: The directory to output the files to.
            soundbite_filename: The name of the soundbite file.
        Returns:
            List[str]: The paths to the output files."""
        soundbite_filepaths=[]
        for i in range(0,10000):
            soundbite_filepath=f"{output_dir}/{soundbite_filename}_{i}.wav"
            if os.path.isfile(soundbite_filepath):
                soundbite_filepaths.append(soundbite_filepath)
        return soundbite_filepaths
    
    def merge_without_converting(self,extension, output_dir,output_filename,soundbite_filename):
        """Merge the wav files without converting them.
        Args:
            extension: The extension of the files to merge.
            output_dir: The directory to output the merged file to.
            output_filename: The name of the merged file.
            soundbite_filename: The name of the soundbite file.
        Returns:
            None"""
        soundbite_filepaths=self.get_output_files(output_dir,soundbite_filename)
        print(f'soundbite_filepaths={soundbite_filepaths}')
        self.merge_wav_files_into_one(extension,output_dir,output_filename,soundbite_filepaths)
        exit()
        
            
    def play_audio(self, audio_path):
        """Play the audio.
        Args:
            audio_path: The path to the audio file."""
        import pyaudio
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
            logger.error(f"Error playing audio: {e}")
            

    def convert_text_to_speech(self, text: str, output_dir: str, output_filename: str):
        """Convert the text to speech.
        Args:
            text: The text to convert to speech.
            output_dir: The directory to output the speech to.
            output_filename: The name of the output file."""
        sentences = self.split_into_sentences_using_nlp(text)
        soundbite_filepaths = self.convert_sentences_to_wav_files(output_filename, output_dir, sentences)
        self.merge_wav_files_into_one("wav", output_dir, output_filename, soundbite_filepaths)
        # delete the individual soundbite files
        for soundbite_filepath in soundbite_filepaths:
            os.remove(soundbite_filepath)
        
        
 