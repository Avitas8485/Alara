import pyaudio
import wave
from typing import List

    

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
            
            
def split_into_sentences_using_nlp(text) -> List[str]:
        """Split the text into sentences using NLP.
        Args:
            text: The text to split into sentences.
        Returns:
            List[str]: The sentences."""
        
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
        
        return merged_sentences
    
