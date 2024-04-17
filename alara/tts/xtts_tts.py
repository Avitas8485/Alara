# Description: This file contains the code for the TextToSpeechSystem class.
import os
import wave
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import soundfile as sf
from alara.lib.logger import logger
from alara.tts.base_tts import BaseTTS
from alara.config.config import cfg


class XttsTTS(BaseTTS):
    """This class contains the code for the TextToSpeechSystem using the XTTS model. 
    It is good but slow. It is not recommended for use in real-time applications, at least on my machine. If you have good hardware, you can use it.
    Preferably, use piper-tts instead. Although, it is not as good as XTTS, it is faster, and can be used in real-time applications even on potato pcs.
    
    Attributes:
        config: The configuration for the XTTS model.
        vocab_path: The path to the vocabulary file.
        speaker_path: The path to the speaker file.
        model_dir: The path to the model directory.
        model: The model to use for text to speech."""
    def __init__(self):
        self.config = XttsConfig()
        self.config.load_json(cfg.XTTS_CONFIG_PATH)
        self.vocab_path = cfg.XTTS_VOCAB_PATH
        self.speaker_path = cfg.XTTS_SPEAKER_PATH
        self.model_dir = cfg.XTTS_MODEL_DIR
        logger.info("TextToSpeechSystem initialized.")
        # make sure the output directory exists
        

    def load_txt_from_file(self, file_path) -> str:
        """Load text from a file.
        Args:
            file_path: The path to the file.
        Returns:
            str: The text from the file."""
        with open(file_path, "r") as file:
            text = file.read()
        return text
            
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
                        
    def synthesize(self,text: str, output_dir: str='alara/tts/outputs', output_filename: str='output.wav'):
        """synthesize the text, play the audio, and then delete the audio file.
        Args:
            text: The text to synthesize.
            output_dir: The directory to output the synthesized text to.
            output_filename: The name of the output file."""
        self.synthesize_to_file(text,output_dir,output_filename)
        self.play_audio(f"{output_dir}/{output_filename}")
        os.remove(f"{output_dir}/{output_filename}")
        
        
    def synthesize_to_file(self,text: str, output_dir: str='alara/tts/outputs', output_filename: str='output.wav'):
        """synthesize the text to a file. Does not play the audio.
        Args:
            text: The text to synthesize.
            output_dir: The directory to output the synthesized text to.
            output_filename: The name of the output file."""
        self.model = Xtts.init_from_config(self.config)
        logger.info("Loading model checkpoint...")
        self.model.load_checkpoint(config=self.config,
                                   checkpoint_dir=self.model_dir,
                                   vocab_path=self.vocab_path)
        gpt_cond_latent, speaker_embedding = self.model.get_conditioning_latents(
                audio_path=[self.speaker_path]
            )
        logger.info("Synthesizing text...")
        out = self.model.inference(
                text=text,
                gpt_cond_latent=gpt_cond_latent,
                speaker_embedding=speaker_embedding,
                language="en",
                enable_text_splitting=True
            )
        logger.info("Synthesis complete.")
        sf.write(f"{output_dir}/{output_filename}", out["wav"], 24000)
        
        
        
 
 
 
