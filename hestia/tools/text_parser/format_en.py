# Description: This script is used to convert numbers, dates, and times in a text to words that the TTS system can read.
import re
from datetime import datetime
from num2words import num2words
from typing import Callable

class Patterns:
    number = re.compile(r'\b-?\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?(?:e-?\d+)?\b')
    date = re.compile(r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{2,4}[-/]\d{1,2}[-/]\d{1,2}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4})\b')
    time = re.compile(r'\b(?:\d{1,2}:\d{2}(?::\d{2})?(?:\s?[ap]m)?|\d{2}:\d{2}(?::\d{2})?(?:\s?[ap]m)?(?:\s?[A-Z]{3})?)\b')


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
            dt = datetime.strptime(dt, "%Y-%m-%d")
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
        text = Converter.replace_matches(Patterns.time, lambda x: Converter.time(datetime.strptime(x, "%H:%M")), text)
        text = Converter.replace_matches(Patterns.number, lambda x: Converter.number(int(x)), text)
        return text
    

if __name__ == "__main__":
    text_chunk = """It is 9:00 AM. Today is 02/23/2004 and the weather is 72 degrees Fahrenheit.
To make a delicious chocolate cake, you'll need the following ingredients:
1 cup (240 ml) all-purpose flour
1/2 cup (100 g) unsweetened cocoa powder
1 1/2 cups (300 g) granulated sugar
3/4 cups (180 ml) milk
1/2 cup (120 g) vegetable oil
2 teaspoons baking soda
1 teaspoon baking powder
1 teaspoon salt
2 large eggs
1 teaspoon vanilla extract
For the frosting:
1/2 cup (1 stick or 113 g) unsalted butter, softened
3 cups (480 g) powdered sugar
2 tablespoons heavy cream or milk
2 teaspoons vanilla extract
1/2 cup (60 g) unsweetened cocoa powder
Start by preheating your oven to 350°F (180°C). Grease and lightly flour two 8-inch (20 cm) round baking pans or line them with baking parchment. Set aside.
In a large bowl, whisk together the flour, cocoa powder, sugar, baking soda, baking powder, and salt. Create a well in the center of the dry ingredients and set aside.
In another bowl, whisk together the milk, vegetable oil, eggs, and vanilla extract until well combined. Pour this wet mixture into the well of dry ingredients and stir until just combined. Do not overmix the batter or your cake may be tough.
Divide the batter between the prepared pans and bake for 25-30 minutes or until a toothpick inserted into the center comes out clean or with a few moist crumbs. Allow the cakes to cool completely before frosting them.
For the frosting, beat together the softened butter and powdered sugar until smooth and creamy. Add the heavy cream or milk and vanilla extract and beat until fluffy and smooth. Finally, stir in the unsweetened cocoa powder until well combined.
Once your cakes have cooled, spread a thin layer of frosting on one layer and place the second layer on top. Spread the remaining frosting on top and around the sides of the cake for a smooth and even finish. Enjoy your homemade chocolate cake!"""
    print(Converter.convert_in_text(text_chunk))