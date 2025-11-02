"""
Games Manager - Trivia, word games, quotes, fun activities
"""

import logging
import random
import requests

logger = logging.getLogger(__name__)


class GamesManager:
    """Manage fun and games features"""

    def __init__(self):
        """Initialize games manager"""
        logger.info("Games Manager initialized")

    def get_trivia_question(self, category=None, difficulty=None):
        """Get trivia question from Open Trivia Database"""
        try:
            url = "https://opentdb.com/api.php"
            params = {'amount': 1}

            if category:
                # Category mapping (some common ones)
                categories = {
                    'general': 9, 'books': 10, 'film': 11, 'music': 12,
                    'television': 14, 'video games': 15, 'science': 17,
                    'computers': 18, 'math': 19, 'sports': 21, 'geography': 22,
                    'history': 23, 'animals': 27
                }
                cat_id = categories.get(category.lower())
                if cat_id:
                    params['category'] = cat_id

            if difficulty and difficulty.lower() in ['easy', 'medium', 'hard']:
                params['difficulty'] = difficulty.lower()

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            if data.get('response_code') != 0 or not data.get('results'):
                return "Couldn't get trivia question. Try again."

            question_data = data['results'][0]
            question = question_data['question']
            correct = question_data['correct_answer']
            incorrect = question_data['incorrect_answers']

            # Combine and shuffle answers
            all_answers = [correct] + incorrect
            random.shuffle(all_answers)

            # Format question
            result = f"Trivia question: {question}. "
            result += f"Answers: {', '.join(all_answers)}. "
            result += f"(The correct answer is: {correct})"

            logger.info("Trivia question retrieved")
            return result

        except Exception as e:
            logger.error(f"Trivia error: {e}")
            return "Couldn't get trivia question"

    def get_quote(self, category='inspirational'):
        """Get random quote"""
        try:
            # Using quotable.io API
            url = "https://api.quotable.io/random"

            # Tag mapping
            tags = {
                'inspirational': 'inspirational',
                'motivational': 'inspirational',
                'funny': 'humorous',
                'wisdom': 'wisdom',
                'life': 'life',
                'success': 'success',
                'happiness': 'happiness',
                'love': 'love',
                'friendship': 'friendship'
            }

            tag = tags.get(category.lower())
            params = {}
            if tag:
                params['tags'] = tag

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            quote_text = data.get('content', '')
            author = data.get('author', 'Unknown')

            result = f'"{quote_text}" - {author}'

            logger.info(f"Quote retrieved: {author}")
            return result

        except Exception as e:
            logger.error(f"Quote error: {e}")
            # Fallback to built-in quotes
            return self._get_fallback_quote()

    def _get_fallback_quote(self):
        """Get quote from built-in list"""
        quotes = [
            ("The only way to do great work is to love what you do.", "Steve Jobs"),
            ("Innovation distinguishes between a leader and a follower.", "Steve Jobs"),
            ("Life is what happens when you're busy making other plans.", "John Lennon"),
            ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
            ("It is during our darkest moments that we must focus to see the light.", "Aristotle"),
            ("The only impossible journey is the one you never begin.", "Tony Robbins"),
            ("In the end, it's not the years in your life that count. It's the life in your years.", "Abraham Lincoln"),
            ("Life is either a daring adventure or nothing at all.", "Helen Keller")
        ]

        quote, author = random.choice(quotes)
        return f'"{quote}" - {author}'

    def play_20_questions(self):
        """Start 20 questions game"""
        things = [
            'elephant', 'computer', 'pizza', 'bicycle', 'guitar',
            'mountain', 'ocean', 'tree', 'book', 'clock',
            'camera', 'phone', 'car', 'airplane', 'rainbow'
        ]

        thing = random.choice(things)

        result = "I'm thinking of something. You have 20 questions to guess it. "
        result += "Ask yes or no questions. "
        result += f"(Hint: The answer is {thing})"

        logger.info(f"20 Questions started: {thing}")
        return result

    def word_of_the_day(self):
        """Get word of the day"""
        try:
            # Wordnik API (requires API key, using fallback)
            # For now, use a curated list
            words = [
                ("serendipity", "The occurrence of events by chance in a happy or beneficial way"),
                ("ephemeral", "Lasting for a very short time"),
                ("petrichor", "The pleasant smell that accompanies the first rain after a dry spell"),
                ("eloquent", "Fluent or persuasive in speaking or writing"),
                ("luminous", "Full of or shedding light; bright or shining"),
                ("ethereal", "Extremely delicate and light in a way that seems too perfect for this world"),
                ("mellifluous", "Sweet or musical; pleasant to hear"),
                ("ubiquitous", "Present, appearing, or found everywhere"),
                ("resplendent", "Attractive and impressive through being richly colorful or sumptuous"),
                ("ephemeral", "Lasting for a very short time; transitory")
            ]

            word, definition = random.choice(words)

            result = f"Word of the day: {word}. "
            result += f"Definition: {definition}"

            logger.info(f"Word of the day: {word}")
            return result

        except Exception as e:
            logger.error(f"Word of day error: {e}")
            return "Couldn't get word of the day"

    def riddle(self):
        """Get a riddle"""
        riddles = [
            ("What has keys but no locks, space but no room, and you can enter but can't go inside?", "A keyboard"),
            ("What comes once in a minute, twice in a moment, but never in a thousand years?", "The letter M"),
            ("I speak without a mouth and hear without ears. I have no body, but come alive with wind. What am I?", "An echo"),
            ("The more you take, the more you leave behind. What am I?", "Footsteps"),
            ("What can travel around the world while staying in a corner?", "A stamp"),
            ("What has a head and a tail but no body?", "A coin"),
            ("What gets wet while drying?", "A towel"),
            ("What can you catch but not throw?", "A cold"),
            ("What runs but never walks, has a mouth but never talks?", "A river"),
            ("What has hands but can't clap?", "A clock")
        ]

        riddle_q, riddle_a = random.choice(riddles)

        result = f"Riddle: {riddle_q} "
        result += f"(Answer: {riddle_a})"

        logger.info("Riddle generated")
        return result

    def joke(self):
        """Get a random joke"""
        try:
            # Using JokeAPI
            url = "https://v2.jokeapi.dev/joke/Any"
            params = {'safe-mode': ''}  # Family-friendly

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            if data.get('type') == 'single':
                joke_text = data.get('joke', '')
            elif data.get('type') == 'twopart':
                setup = data.get('setup', '')
                delivery = data.get('delivery', '')
                joke_text = f"{setup} ... {delivery}"
            else:
                return self._get_fallback_joke()

            logger.info("Joke retrieved")
            return joke_text

        except Exception as e:
            logger.error(f"Joke error: {e}")
            return self._get_fallback_joke()

    def _get_fallback_joke(self):
        """Get joke from built-in list"""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a bear with no teeth? A gummy bear!",
            "Why did the bicycle fall over? It was two tired!",
            "What do you call a fake noodle? An impasta!",
            "How do you organize a space party? You planet!",
            "Why can't you give Elsa a balloon? Because she will let it go!"
        ]

        return random.choice(jokes)

    def magic_8_ball(self, question):
        """Magic 8-ball responses"""
        responses = [
            "It is certain",
            "Without a doubt",
            "Yes definitely",
            "You may rely on it",
            "As I see it, yes",
            "Most likely",
            "Outlook good",
            "Yes",
            "Signs point to yes",
            "Reply hazy, try again",
            "Ask again later",
            "Better not tell you now",
            "Cannot predict now",
            "Concentrate and ask again",
            "Don't count on it",
            "My reply is no",
            "My sources say no",
            "Outlook not so good",
            "Very doubtful"
        ]

        response = random.choice(responses)

        result = f"Magic 8-Ball says: {response}"

        logger.info(f"Magic 8-ball: {response}")
        return result

    def yes_or_no(self):
        """Random yes/no decision"""
        answer = random.choice(["Yes", "No"])
        logger.info(f"Yes/No: {answer}")
        return f"The answer is: {answer}"
