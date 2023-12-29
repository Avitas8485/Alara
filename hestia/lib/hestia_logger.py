import logging



class Singleton(type):
    """Singleton metaclass."""
    _instances = {}

    def __init__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__init__(*args, **kwargs)
        return cls._instances[cls]


class HestiaLogger(metaclass=Singleton):
    """Singleton class for logging."""
    def __init__(self, logger_name='Hestia', log_level=logging.DEBUG):
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger(logger_name)
            self.logger.setLevel(log_level)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)

            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S %Z')

            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def debug(self, message, *args):
        """Log a debug message."""
        self.logger.debug(message, *args)

    def info(self, message, *args):
        """Log an info message."""
        self.logger.info(message, *args)

    def warning(self, message, *args):
        """Log a warning message."""
        self.logger.warning(message, *args)

    def error(self, message, *args):
        """Log an error message."""
        self.logger.error(message, *args)

    def critical(self, message, *args):
        """Log a critical message."""
        self.logger.critical(message, *args)
       
       
logger = HestiaLogger().logger
