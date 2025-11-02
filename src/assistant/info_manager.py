"""
Information & Lookup Manager - Weather, news, Wikipedia, definitions, conversions
"""

import os
import json
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class InfoManager:
    """Manage information lookup features"""

    def __init__(self):
        """Initialize information manager"""

        # API keys from environment
        self.openweather_api_key = os.getenv('OPENWEATHER_API_KEY')
        self.news_api_key = os.getenv('NEWS_API_KEY')

        # Default location (can be overridden)
        self.default_location = os.getenv('DEFAULT_LOCATION', 'New York')

        logger.info("Information Manager initialized")

    def get_weather(self, location=None):
        """Get current weather for a location"""
        if not self.openweather_api_key:
            return "Weather service not configured. Set OPENWEATHER_API_KEY environment variable. Get a free key at https://openweathermap.org/api"

        location = location or self.default_location

        try:
            # OpenWeatherMap current weather API
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': location,
                'appid': self.openweather_api_key,
                'units': 'imperial'  # Fahrenheit
            }

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            # Extract key info
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            description = data['weather'][0]['description']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']

            weather_report = (
                f"In {location}, it's {temp:.0f}°F and {description}. "
                f"Feels like {feels_like:.0f}°. "
                f"Humidity {humidity}%, wind {wind_speed:.0f} mph."
            )

            logger.info(f"Weather retrieved for {location}")
            return weather_report

        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API error: {e}")
            return f"Couldn't get weather for {location}. Check your internet connection."

    def get_forecast(self, location=None, days=3):
        """Get weather forecast"""
        if not self.openweather_api_key:
            return "Weather service not configured."

        location = location or self.default_location

        try:
            url = "http://api.openweathermap.org/data/2.5/forecast"
            params = {
                'q': location,
                'appid': self.openweather_api_key,
                'units': 'imperial',
                'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
            }

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            # Get daily summaries
            forecast_text = f"Forecast for {location}: "

            # Group by day and get high/low
            daily_data = {}
            for item in data['list'][:days * 8]:
                date = datetime.fromtimestamp(item['dt']).strftime('%A')
                temp = item['main']['temp']
                desc = item['weather'][0]['description']

                if date not in daily_data:
                    daily_data[date] = {'temps': [], 'desc': desc}
                daily_data[date]['temps'].append(temp)

            # Format forecast
            for day, info in list(daily_data.items())[:days]:
                high = max(info['temps'])
                low = min(info['temps'])
                forecast_text += f"{day}: {high:.0f}°/{low:.0f}°, {info['desc']}. "

            logger.info(f"Forecast retrieved for {location}")
            return forecast_text.strip()

        except requests.exceptions.RequestException as e:
            logger.error(f"Forecast API error: {e}")
            return "Couldn't get forecast."

    def get_news(self, topic=None, count=3):
        """Get latest news headlines"""
        if not self.news_api_key:
            return "News service not configured. Set NEWS_API_KEY environment variable. Get a free key at https://newsapi.org"

        try:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                'apiKey': self.news_api_key,
                'country': 'us',
                'pageSize': count
            }

            if topic:
                params['q'] = topic

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            if data.get('status') != 'ok' or not data.get('articles'):
                return "No news articles found."

            # Format headlines
            news_text = f"Top {count} headlines"
            if topic:
                news_text += f" about {topic}"
            news_text += ": "

            for i, article in enumerate(data['articles'][:count], 1):
                title = article.get('title', 'Unknown')
                news_text += f"{i}. {title}. "

            logger.info(f"News retrieved (topic: {topic or 'general'})")
            return news_text.strip()

        except requests.exceptions.RequestException as e:
            logger.error(f"News API error: {e}")
            return "Couldn't get news. Check your internet connection."

    def search_wikipedia(self, query):
        """Search Wikipedia for information"""
        try:
            # Wikipedia API
            url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(' ', '_')

            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            if data.get('type') == 'disambiguation':
                return f"'{query}' is ambiguous. Please be more specific."

            # Get extract (summary)
            extract = data.get('extract', '')

            if not extract:
                return f"No Wikipedia article found for '{query}'."

            # Limit to first 2-3 sentences for voice
            sentences = extract.split('. ')
            summary = '. '.join(sentences[:2]) + '.'

            logger.info(f"Wikipedia search for: {query}")
            return summary

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return f"No Wikipedia article found for '{query}'."
            logger.error(f"Wikipedia API error: {e}")
            return f"Couldn't search Wikipedia for '{query}'."
        except requests.exceptions.RequestException as e:
            logger.error(f"Wikipedia API error: {e}")
            return "Wikipedia search failed."

    def define_word(self, word):
        """Get definition of a word"""
        try:
            # Free Dictionary API
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            if not data or len(data) == 0:
                return f"No definition found for '{word}'."

            # Get first definition
            entry = data[0]
            word_text = entry.get('word', word)
            meanings = entry.get('meanings', [])

            if not meanings:
                return f"No definition found for '{word}'."

            # Get first meaning
            first_meaning = meanings[0]
            part_of_speech = first_meaning.get('partOfSpeech', '')
            definitions = first_meaning.get('definitions', [])

            if not definitions:
                return f"No definition found for '{word}'."

            definition = definitions[0].get('definition', '')
            example = definitions[0].get('example', '')

            result = f"{word_text}"
            if part_of_speech:
                result += f" ({part_of_speech})"
            result += f": {definition}"

            if example:
                result += f" Example: {example}"

            logger.info(f"Definition retrieved for: {word}")
            return result

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return f"No definition found for '{word}'."
            logger.error(f"Dictionary API error: {e}")
            return f"Couldn't define '{word}'."
        except requests.exceptions.RequestException as e:
            logger.error(f"Dictionary API error: {e}")
            return "Dictionary lookup failed."

    def convert_units(self, value, from_unit, to_unit):
        """Convert between units"""
        try:
            value = float(value)
        except ValueError:
            return f"Invalid number: {value}"

        from_unit = from_unit.lower()
        to_unit = to_unit.lower()

        # Conversion factors to base units
        conversions = {
            # Length (to meters)
            'meter': 1, 'meters': 1, 'm': 1,
            'kilometer': 1000, 'kilometers': 1000, 'km': 1000,
            'centimeter': 0.01, 'centimeters': 0.01, 'cm': 0.01,
            'millimeter': 0.001, 'millimeters': 0.001, 'mm': 0.001,
            'mile': 1609.34, 'miles': 1609.34, 'mi': 1609.34,
            'yard': 0.9144, 'yards': 0.9144, 'yd': 0.9144,
            'foot': 0.3048, 'feet': 0.3048, 'ft': 0.3048,
            'inch': 0.0254, 'inches': 0.0254, 'in': 0.0254,

            # Weight (to kilograms)
            'kilogram': 1, 'kilograms': 1, 'kg': 1,
            'gram': 0.001, 'grams': 0.001, 'g': 0.001,
            'pound': 0.453592, 'pounds': 0.453592, 'lb': 0.453592, 'lbs': 0.453592,
            'ounce': 0.0283495, 'ounces': 0.0283495, 'oz': 0.0283495,

            # Temperature (special case)
            'celsius': None, 'c': None,
            'fahrenheit': None, 'f': None,
            'kelvin': None, 'k': None,

            # Volume (to liters)
            'liter': 1, 'liters': 1, 'l': 1,
            'milliliter': 0.001, 'milliliters': 0.001, 'ml': 0.001,
            'gallon': 3.78541, 'gallons': 3.78541, 'gal': 3.78541,
            'quart': 0.946353, 'quarts': 0.946353, 'qt': 0.946353,
            'pint': 0.473176, 'pints': 0.473176, 'pt': 0.473176,
            'cup': 0.236588, 'cups': 0.236588,
            'fluid_ounce': 0.0295735, 'fluid_ounces': 0.0295735, 'fl_oz': 0.0295735,
        }

        # Handle temperature conversions specially
        if from_unit in ['celsius', 'c', 'fahrenheit', 'f', 'kelvin', 'k']:
            return self._convert_temperature(value, from_unit, to_unit)

        # Get conversion factors
        if from_unit not in conversions or to_unit not in conversions:
            return f"Unknown units: {from_unit} or {to_unit}"

        from_factor = conversions[from_unit]
        to_factor = conversions[to_unit]

        if from_factor is None or to_factor is None:
            return "Cannot convert between these unit types"

        # Convert to base unit, then to target unit
        base_value = value * from_factor
        result = base_value / to_factor

        logger.info(f"Unit conversion: {value} {from_unit} = {result} {to_unit}")
        return f"{value} {from_unit} equals {result:.2f} {to_unit}"

    def _convert_temperature(self, value, from_unit, to_unit):
        """Convert temperature units"""
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()

        # Normalize unit names
        if from_unit in ['c', 'celsius']:
            from_unit = 'celsius'
        elif from_unit in ['f', 'fahrenheit']:
            from_unit = 'fahrenheit'
        elif from_unit in ['k', 'kelvin']:
            from_unit = 'kelvin'

        if to_unit in ['c', 'celsius']:
            to_unit = 'celsius'
        elif to_unit in ['f', 'fahrenheit']:
            to_unit = 'fahrenheit'
        elif to_unit in ['k', 'kelvin']:
            to_unit = 'kelvin'

        # Convert to Celsius first
        if from_unit == 'celsius':
            celsius = value
        elif from_unit == 'fahrenheit':
            celsius = (value - 32) * 5/9
        elif from_unit == 'kelvin':
            celsius = value - 273.15
        else:
            return f"Unknown temperature unit: {from_unit}"

        # Convert from Celsius to target
        if to_unit == 'celsius':
            result = celsius
        elif to_unit == 'fahrenheit':
            result = (celsius * 9/5) + 32
        elif to_unit == 'kelvin':
            result = celsius + 273.15
        else:
            return f"Unknown temperature unit: {to_unit}"

        logger.info(f"Temperature conversion: {value}° {from_unit} = {result}° {to_unit}")
        return f"{value}° {from_unit} equals {result:.2f}° {to_unit}"

    def convert_currency(self, amount, from_currency, to_currency):
        """Convert currency (using free exchange rate API)"""
        try:
            amount = float(amount)
        except ValueError:
            return f"Invalid amount: {amount}"

        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        try:
            # Using exchangerate-api.com (free tier)
            url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"

            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            if 'rates' not in data or to_currency not in data['rates']:
                return f"Couldn't convert {from_currency} to {to_currency}"

            rate = data['rates'][to_currency]
            result = amount * rate

            logger.info(f"Currency conversion: {amount} {from_currency} = {result} {to_currency}")
            return f"{amount:.2f} {from_currency} equals {result:.2f} {to_currency}"

        except requests.exceptions.RequestException as e:
            logger.error(f"Currency API error: {e}")
            return "Currency conversion failed. Check your internet connection."
