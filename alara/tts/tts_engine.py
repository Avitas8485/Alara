from .piper_tts import PiperTTS
from .xtts_tts import XttsTTS
from enum import Enum


class TtsType(Enum):
    piper = 'piper'
    xtts = 'xtts'
class TTSEngine:
    @staticmethod
    def load_tts(tts_type: TtsType=TtsType.piper):
        if tts_type == TtsType.piper:
            return PiperTTS()
        elif tts_type == TtsType.xtts:
            return XttsTTS()
        else:
            raise ValueError('Invalid TTS type')
    
