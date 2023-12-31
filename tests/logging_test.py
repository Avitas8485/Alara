import unittest
import logging
from hestia.lib.hestia_logger import HestiaLogger

class TestHestiaLogger(unittest.TestCase):
    def setUp(self):
        self.logger = HestiaLogger('TestLogger')

    def test_debug(self):
        with self.assertLogs('TestLogger', level='DEBUG') as cm:
            self.logger.debug('debug message')
        self.assertIn('DEBUG:TestLogger:debug message', cm.output)

    def test_info(self):
        with self.assertLogs('TestLogger', level='INFO') as cm:
            self.logger.info('info message')
        self.assertIn('INFO:TestLogger:info message', cm.output)

    def test_warning(self):
        with self.assertLogs('TestLogger', level='WARNING') as cm:
            self.logger.warning('warning message')
        self.assertIn('WARNING:TestLogger:warning message', cm.output)

    def test_error(self):
        with self.assertLogs('TestLogger', level='ERROR') as cm:
            self.logger.error('error message')
        self.assertIn('ERROR:TestLogger:error message', cm.output)

    def test_critical(self):
        with self.assertLogs('TestLogger', level='CRITICAL') as cm:
            self.logger.critical('critical message')
        self.assertIn('CRITICAL:TestLogger:critical message', cm.output)

if __name__ == '__main__':
    unittest.main()