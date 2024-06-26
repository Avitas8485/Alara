

class Singleton(type):
    """A singleton metaclass.
    Attributes:
        _instances: dict: The instances of the class."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
    
