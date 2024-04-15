# Description: This script is used to convert numbers, dates, and times in a text to words that the TTS system can read.
import re
from datetime import datetime
from num2words import num2words
from typing import Callable
from dateutil.parser import parse

class Patterns:
    number = re.compile(r'\b-?\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?(?:e-?\d+)?\b')
    date = re.compile(r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{2,4}[-/]\d{1,2}[-/]\d{1,2}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}|(?:\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}))\b')
    time = re.compile(r'\b(?:\d{1,2}:\d{2}(?::\d{2})?(?:\s?[ap]m)?|\d{2}:\d{2}(?::\d{2})?(?:\s?[ap]m)?(?:\s?[A-Z]{3})?|(\d{1,2}\s?(?:am|pm)))\b')


class Converter:
    @staticmethod
    def number(number: int|float) -> str:
        """Convert a number to words."""
        return num2words(number)
    
    @staticmethod
    def time(dt: datetime, use_24_hour: bool = False, use_ampm: bool = False) -> str:
        """Format datetime to words that the TTS system can read.
        eg 3:14 PM -> three fourteen PM
        """
        if use_24_hour:
            string = dt.strftime("%H:%M")
        else:
            string = dt.strftime("%I:%M %p" if use_ampm else "%I:%M").lstrip("0")
    
        parts = string.split(' ')
        hour, minute = parts[0].split(':')
        ampm = parts[1] if len(parts) > 1 else ''
        natural_language = num2words(int(hour))
    
        if minute != "00":
            natural_language += " " + num2words(int(minute))
        else:
            natural_language += " o'clock"
    
        if use_ampm:
            natural_language += " " + ampm
    
        return natural_language
    
    @staticmethod
    def date(dt: datetime) -> str:
        """Format date to words that the TTS system can read.
        eg 2022-01-01 -> January first twenty twenty two
        """
        if isinstance(dt, str):
            dt = parse(dt)
        day = num2words(dt.day, to='ordinal')
        month = dt.strftime("%B")
        year = num2words(dt.year)
        return f"{day} of {month}, {year}"
    
    @staticmethod
    def replace_matches(pattern: re.Pattern, convert_func: Callable, text: str) -> str:
        """Replace matches in the text using the provided conversion function."""
        def repl(match):
            try:
                return convert_func(match.group(0))
            except ValueError as e:
                print(f"Error converting match: {e}")
                return match.group(0)
    
        return pattern.sub(repl, text)
    
    @staticmethod
    def convert_in_text(text: str) -> str:
        """Convert numbers, dates, and times in the text to words."""
        text = Converter.replace_matches(Patterns.date, Converter.date, text)
        text = Converter.replace_matches(Patterns.time, lambda x: Converter.time(parse(x)), text)
        text = Converter.replace_matches(Patterns.number, lambda x: Converter.number(int(x)), text)
        return text
    

if __name__ == "__main__":
    text_chunk = """Time pattern 1: 3:14 PM
    Time pattern 2: 15:14
    Time pattern 3: 3:14:15 PM
    Time pattern 4: 15:14:15
    Date pattern 1: 2022-01-01
    Date pattern 2: 01/01/2022
    Date pattern 3: January 1, 2022
    Number pattern 1: 123.45
    Number pattern 2: 123,456.78
    Number pattern 3: 123456.78
    Number pattern 4: 123456
    Number pattern 5: 123456789
    """
    print(Converter.convert_in_text(text_chunk))