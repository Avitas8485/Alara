import logging
from collections import deque
from rich.console import Console
from rich.logging import RichHandler
from rich.pretty import install as pretty_install
from rich.theme import Theme
from rich.traceback import install as traceback_install
from alara.lib.singleton import Singleton


class Logger(metaclass=Singleton):
    """Class to manage the logger.
    Attributes:
        logger_name: str: The name of the logger. Default is 'Alara'.
        log_level: int: The log level. Default is logging.DEBUG."""
    def __init__(self, logger_name='Alara', log_level=logging.DEBUG):
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger(logger_name)
            self.logger.setLevel(log_level)
            self.setup_logging()

    def setup_logging(self, log_level=logging.DEBUG,
                      log_time_format='%Y-%m-%d %H:%M:%S', theme=None):
        """Setup the logging.
        Args:
            log_level: int: The log level. Default is logging.DEBUG.
            log_time_format: str: The log time format. Default is '%Y-%m-%d %H:%M:%S'.
            theme: dict: The theme for the console. Default is None."""
        if theme is None:
            theme = {
                "traceback.border": "black",
                "traceback.border.syntax_error": "black",
                "inspect.value.border": "black"}
            console = Console(log_time=True,
                              log_time_format=log_time_format,
                              theme=Theme(theme))
        pretty_install(console=console)
        traceback_install(console=console, extra_lines=1, max_frames=10,
                          width=console.width, word_wrap=False,
                          indent_guides=False, suppress=[])
        rh = RichHandler(show_time=True, omit_repeated_times=False,
                         show_level=True, show_path=False, markup=False,
                         rich_tracebacks=True, log_time_format=log_time_format,
                         level=log_level, console=console)
        file_handler = logging.FileHandler('hestia.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(rh)
        self.logger.addHandler(file_handler)


class RingBuffer(logging.StreamHandler):
    """Class to manage the ring buffer.
    Attributes:
        capacity: int: The capacity of the buffer.
        buffer: deque: The buffer.
        formatter: logging.Formatter: The formatter."""
    def __init__(self, capacity):
        super().__init__()
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)
        self.formatter = logging.Formatter(
            '{ "asctime":"%(asctime)s", "created":%(created)f, \
            "facility":"%(name)s", "pid":%(process)d, "tid":%(thread)d, \
            "level":"%(levelname)s", "module":"%(module)s", \
            "func":"%(funcName)s", "msg":"%(message)s" }')

    def emit(self, record):
        """Emit the record.
        Args:
            record: The record to emit."""
        msg = self.format(record)
        self.buffer.append(msg)

    def get(self):
        return list(self.buffer)


logger = Logger("Alara").logger
