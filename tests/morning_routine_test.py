import os
import unittest
from unittest.mock import patch, mock_open
from hestia.routines.morning.morning_routine import cleanup
from unittest.mock import call

class TestCleanup(unittest.TestCase):
    @patch('os.listdir')
    @patch('os.remove')
    def test_cleanup(self, mock_remove, mock_listdir):
        # Mock the files in the directories
        mock_listdir.side_effect = [
            ['file1.wav', 'file2.wav', 'file3.txt'],  # hestia/text_to_speech/outputs
            ['report1.txt', 'report2.txt', 'report3.pdf'],  # hestia/tools/reports/news
            ['weather1.txt', 'weather2.txt', 'weather3.pdf']  # hestia/tools/reports/weather
        ]

        cleanup()

        # Check if os.remove was called with the correct arguments
        calls = [
            call('hestia/text_to_speech/outputs/file1.wav'),
            call('hestia/text_to_speech/outputs/file2.wav'),
            call('hestia/tools/reports/news/report1.txt'),
            call('hestia/tools/reports/news/report2.txt'),
            call('hestia/tools/reports/weather/weather1.txt'),
            call('hestia/tools/reports/weather/weather2.txt')
        ]
        mock_remove.assert_has_calls(calls, any_order=True)

if __name__ == '__main__':
    unittest.main()