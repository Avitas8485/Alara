import logging
from collections import deque
from rich.console import Console
from rich.logging import RichHandler
from rich.pretty import install as pretty_install
from rich.theme import Theme
from rich.traceback import install as traceback_install
from alara.lib.singleton import Singleton




class HestiaLogger(metaclass=Singleton):
    def __init__(self, logger_name='Hestia', log_level=logging.DEBUG):
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger(logger_name)
            self.logger.setLevel(log_level)
            self.setup_logging()

    def setup_logging(self, log_level=logging.DEBUG,
                      log_time_format='%Y-%m-%d %H:%M:%S', theme=None):
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
        msg = self.format(record)
        self.buffer.append(msg)

    def get(self):
        return list(self.buffer)


logger = HestiaLogger("Alara").logger
