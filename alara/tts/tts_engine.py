from .piper_tts import PiperTTS
from .xtts_tts import XttsTTS
from alara.tools.base_tool import Tool, ToolStatus




class TTS(Tool):
    def __init__(self, tts_engine: str='piper'):
        self.tts_engine = tts_engine
        self.output_dir = 'hestia/tts/outputs'
        self.output_filename = 'output.wav'
        self.name = "text_to_speech engine"
        self.description = "Convert text to speech"
        self.usage = "text_to_speech [text] [to_file] [engine]"
        self.dependencies = {}
        self.status = ToolStatus.UNKNOWN
    
    def get_tts_engine(self, engine: str='piper'):
        if engine == 'piper':
            return PiperTTS()
        elif engine == 'xtts':
            return XttsTTS()
        else:
            raise ValueError(f"Invalid TTS engine: {engine}")
        
    def synthesize(self, text: str, engine: str='piper'):
        tts = self.get_tts_engine(engine)
        return tts.synthesize(text)
    
    def synthesize_to_file(self, text: str, engine: str='piper'):
        tts = self.get_tts_engine(engine)
        return tts.synthesize_to_file(text=text, output_dir=self.output_dir, output_filename=self.output_filename)
    
    def _run(self, text: str, to_file: bool=False, engine: str='piper'):
        if to_file:
            self.synthesize_to_file(text, engine)
        else:
            self.synthesize(text, engine)
            
            
            
    
    