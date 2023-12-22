# Description: This file contains the code for the TextToSpeechSystem class.
import os
import re
import subprocess
from pydub import AudioSegment
import wave
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import soundfile as sf

class TextToSpeechSystem:
    def __init__(self):
        self.config = XttsConfig()
        self.config.load_json("C:/Users/avity/Projects/models/tts/xtts_v2-001/config.json")
        self.model = Xtts.init_from_config(self.config)
        self.vocab_path = "C:/Users/avity/Projects/models/tts/xtts_v2-001/vocab.json"
        self.speaker_path = "automation/text_to_speech/voice_samples/output_00000017.wav"
        self.model_dir = "C:/Users/avity/Projects/models/tts/xtts_v2-001/"
        self.model.load_checkpoint(config=self.config, checkpoint_dir=self.model_dir, vocab_path=self.vocab_path)
        
    def split_into_sentences_using_nlp(self,text):
        import nltk
        nltk.download('punkt')
        from nltk.tokenize import sent_tokenize
        sentences = sent_tokenize(text)
        return sentences
    
    def load_txt_from_file(self,file_path):
        with open(file_path, "r") as file:
            text = file.read()
        return text
    
    def split_into_sentences(self,text):
        # Specify regex values.
        alphabets= "([A-Za-z])"
        prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
        suffixes = "(Inc|Ltd|Jr|Sr|Co)"
        starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
        acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
        websites = "[.](com|net|org|io|gov)"
        digits = "([0-9])"

        # Perform conversion.
        text = " " + text + "  "
        text = text.replace("\n"," ")
        text = re.sub(prefixes,"\\1<prd>",text)
        text = re.sub(websites,"<prd>\\1",text)
        text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2",text)
        if "..." in text: text = text.replace("...","<prd><prd><prd>")
        if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
        text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
        text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
        text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
        text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
        text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
        text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
        text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
        if "”" in text: text = text.replace(".”","”.")
        if "\"" in text: text = text.replace(".\"","\".")
        if "!" in text: text = text.replace("!\"","\"!")
        if "?" in text: text = text.replace("?\"","\"?")
        text = text.replace(".",".<stop>")
        text = text.replace("?","?<stop>")
        text = text.replace("!","!<stop>")
        text = text.replace("<prd>",".")

        sentences = text.split("<stop>")
        sentences = sentences[:-1]
        sentences = [s.strip() for s in sentences]
        return sentences
    
    def convert_sentences_to_wav_files(self,filename: str, output_dir: str, sentences: list):
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
        return soundbite_filepaths
    
    def merge_wav_files_into_one(self,format: str,output_dir:str,output_filename:str,soundbite_filepaths:list):
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

        combined_sounds.export(output_filepath, format=format)

    def get_output_files(self,output_dir,soundbite_filename):
        soundbite_filepaths=[]
        for i in range(0,10000):
            soundbite_filepath=f"{output_dir}/{soundbite_filename}_{i}.wav"
            if os.path.isfile(soundbite_filepath):
                soundbite_filepaths.append(soundbite_filepath)
        return soundbite_filepaths
    
    def merge_without_converting(self,extension, output_dir,output_filename,soundbite_filename):
        soundbite_filepaths=self.get_output_files(output_dir,soundbite_filename)
        print(f'soundbite_filepaths={soundbite_filepaths}')
        self.merge_wav_files_into_one(extension,output_dir,output_filename,soundbite_filepaths)
        exit()
        
            
    def play_audio(self, audio_path):
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
            print(f"Error: {e}")
            

    def convert_text_to_speech(self, text: str, output_dir: str, output_filename: str):
        sentences = self.split_into_sentences(text)
        soundbite_filepaths = self.convert_sentences_to_wav_files(output_filename, output_dir, sentences)
        self.merge_wav_files_into_one("wav", output_dir, output_filename, soundbite_filepaths)
        self.play_audio(f"{output_dir}/{output_filename}.wav")
        
    def convert_text_to_speech_using_nlp(self, text: str, output_dir: str, output_filename: str):
        sentences = self.split_into_sentences_using_nlp(text)
        soundbite_filepaths = self.convert_sentences_to_wav_files(output_filename, output_dir, sentences)
        self.merge_wav_files_into_one("wav", output_dir, output_filename, soundbite_filepaths)
        self.play_audio(f"{output_dir}/{output_filename}.wav")
        

if __name__ == "__main__":
    tts = TextToSpeechSystem()
    text = tts.load_txt_from_file("input.txt")
    tts.convert_text_to_speech_using_nlp(text, "automation/text_to_speech/outputs", "output")