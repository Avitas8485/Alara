from abc import ABC, ABCMeta, abstractmethod


class SingletonMeta(ABCMeta):
    """Singleton metaclass."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class BaseTTS(ABC, metaclass=SingletonMeta):
    @abstractmethod
    def synthesize(self, text: str):
        pass
    

    @abstractmethod
    def synthesize_to_file(self, text: str, output_dir: str, output_filename: str):
        pass
    

