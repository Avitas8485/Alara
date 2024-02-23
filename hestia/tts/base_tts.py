from abc import ABC, abstractmethod

class BaseTTS(ABC):
    @abstractmethod
    def synthesize(self, text: str):
        pass

    @abstractmethod
    def synthesize_to_file(self, text: str, output_dir: str, output_filename: str):
        pass

    

