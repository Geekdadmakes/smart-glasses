"""
Quick Tools Manager - Calculator, age calculator, countdown, random generators
"""

import logging
import random
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)


class QuickToolsManager:
    """Manage quick utility tools"""

    def __init__(self):
        """Initialize quick tools manager"""
        logger.info("Quick Tools Manager initialized")

    def calculate(self, expression):
        """Safely evaluate a mathematical expression"""
        try:
            # Remove any potentially dangerous characters
            # Only allow numbers, operators, parentheses, and basic functions
            allowed_chars = set('0123456789+-*/().% ')
            cleaned = ''.join(c for c in expression if c in allowed_chars)

            if not cleaned:
                return "Invalid calculation expression"

            # Use eval with restricted globals/locals for safety
            result = eval(cleaned, {"__builtins__": {}}, {})

            logger.info(f"Calculation: {expression} = {result}")
            return f"{expression} equals {result}"

        except ZeroDivisionError:
            return "Cannot divide by zero"
        except Exception as e:
            logger.error(f"Calculation error: {e}")
            return f"Couldn't calculate '{expression}'. Try a simpler expression."

    def calculate_age(self, birthdate_str):
        """Calculate age from birthdate"""
        try:
            # Try to parse various date formats
            formats = [
                '%Y-%m-%d',   # 2000-01-15
                '%m/%d/%Y',   # 01/15/2000
                '%d/%m/%Y',   # 15/01/2000
                '%B %d, %Y',  # January 15, 2000
                '%b %d, %Y',  # Jan 15, 2000
            ]

            birthdate = None
            for fmt in formats:
                try:
                    birthdate = datetime.strptime(birthdate_str, fmt)
                    break
                except ValueError:
                    continue

            if not birthdate:
                return f"Couldn't parse date '{birthdate_str}'. Try format: YYYY-MM-DD or MM/DD/YYYY"

            today = datetime.now()
            age = today.year - birthdate.year

            # Adjust if birthday hasn't occurred this year yet
            if (today.month, today.day) < (birthdate.month, birthdate.day):
                age -= 1

            # Calculate days until next birthday
            next_birthday = birthdate.replace(year=today.year)
            if next_birthday < today:
                next_birthday = birthdate.replace(year=today.year + 1)

            days_to_birthday = (next_birthday - today).days

            result = f"Age: {age} years old"
            if days_to_birthday > 0:
                result += f". Next birthday in {days_to_birthday} days"

            logger.info(f"Age calculation: {birthdate_str} = {age} years")
            return result

        except Exception as e:
            logger.error(f"Age calculation error: {e}")
            return "Couldn't calculate age"

    def days_until(self, target_date_str):
        """Calculate days until a future date"""
        try:
            # Parse date
            formats = [
                '%Y-%m-%d',
                '%m/%d/%Y',
                '%B %d, %Y',
                '%b %d, %Y',
                '%B %d',      # December 25 (assumes current year)
                '%b %d',      # Dec 25
            ]

            target_date = None
            for fmt in formats:
                try:
                    target_date = datetime.strptime(target_date_str, fmt)
                    # If no year specified, assume current year or next year
                    if target_date.year == 1900:  # Default year from strptime
                        target_date = target_date.replace(year=datetime.now().year)
                        if target_date < datetime.now():
                            target_date = target_date.replace(year=datetime.now().year + 1)
                    break
                except ValueError:
                    continue

            if not target_date:
                return f"Couldn't parse date '{target_date_str}'"

            today = datetime.now()
            days_diff = (target_date - today).days

            if days_diff < 0:
                return f"{target_date_str} was {abs(days_diff)} days ago"
            elif days_diff == 0:
                return f"{target_date_str} is today!"
            elif days_diff == 1:
                return f"{target_date_str} is tomorrow"
            else:
                return f"{days_diff} days until {target_date_str}"

        except Exception as e:
            logger.error(f"Days until error: {e}")
            return "Couldn't calculate days"

    def days_between(self, date1_str, date2_str):
        """Calculate days between two dates"""
        try:
            formats = ['%Y-%m-%d', '%m/%d/%Y', '%B %d, %Y', '%b %d, %Y']

            date1 = None
            date2 = None

            for fmt in formats:
                try:
                    if not date1:
                        date1 = datetime.strptime(date1_str, fmt)
                except ValueError:
                    pass

                try:
                    if not date2:
                        date2 = datetime.strptime(date2_str, fmt)
                except ValueError:
                    pass

            if not date1 or not date2:
                return "Couldn't parse dates"

            days_diff = abs((date2 - date1).days)

            logger.info(f"Days between: {date1_str} and {date2_str} = {days_diff} days")
            return f"{days_diff} days between {date1_str} and {date2_str}"

        except Exception as e:
            logger.error(f"Days between error: {e}")
            return "Couldn't calculate days between dates"

    def flip_coin(self):
        """Flip a coin"""
        result = random.choice(['Heads', 'Tails'])
        logger.info(f"Coin flip: {result}")
        return f"Coin flip: {result}"

    def roll_dice(self, sides=6, count=1):
        """Roll dice"""
        try:
            sides = int(sides)
            count = int(count)

            if sides < 2 or sides > 100:
                return "Dice must have between 2 and 100 sides"

            if count < 1 or count > 10:
                return "You can roll 1 to 10 dice at a time"

            rolls = [random.randint(1, sides) for _ in range(count)]
            total = sum(rolls)

            if count == 1:
                result = f"Rolled a {sides}-sided die: {rolls[0]}"
            else:
                result = f"Rolled {count} {sides}-sided dice: {', '.join(map(str, rolls))}. Total: {total}"

            logger.info(f"Dice roll: {count}d{sides} = {rolls}")
            return result

        except Exception as e:
            logger.error(f"Dice roll error: {e}")
            return "Couldn't roll dice"

    def random_number(self, min_val=1, max_val=100):
        """Generate random number in range"""
        try:
            min_val = int(min_val)
            max_val = int(max_val)

            if min_val >= max_val:
                return "Minimum must be less than maximum"

            number = random.randint(min_val, max_val)

            logger.info(f"Random number: {number} (range {min_val}-{max_val})")
            return f"Random number between {min_val} and {max_val}: {number}"

        except Exception as e:
            logger.error(f"Random number error: {e}")
            return "Couldn't generate random number"

    def percentage(self, part, whole):
        """Calculate what percentage 'part' is of 'whole'"""
        try:
            part = float(part)
            whole = float(whole)

            if whole == 0:
                return "Cannot calculate percentage of zero"

            pct = (part / whole) * 100

            logger.info(f"Percentage: {part} is {pct:.1f}% of {whole}")
            return f"{part} is {pct:.1f}% of {whole}"

        except Exception as e:
            logger.error(f"Percentage error: {e}")
            return "Couldn't calculate percentage"

    def tip_calculator(self, bill_amount, tip_percent=20):
        """Calculate tip and total"""
        try:
            bill = float(bill_amount)
            tip_pct = float(tip_percent)

            if bill < 0:
                return "Bill amount cannot be negative"

            tip_amount = bill * (tip_pct / 100)
            total = bill + tip_amount

            result = f"Bill: ${bill:.2f}, {tip_pct}% tip: ${tip_amount:.2f}, Total: ${total:.2f}"

            logger.info(f"Tip calculation: bill ${bill}, tip {tip_pct}% = ${tip_amount}")
            return result

        except Exception as e:
            logger.error(f"Tip calculation error: {e}")
            return "Couldn't calculate tip"

    def bmi_calculator(self, weight_lbs, height_inches):
        """Calculate BMI (Body Mass Index)"""
        try:
            weight = float(weight_lbs)
            height = float(height_inches)

            if weight <= 0 or height <= 0:
                return "Weight and height must be positive numbers"

            # BMI = (weight in pounds * 703) / (height in inches)^2
            bmi = (weight * 703) / (height ** 2)

            # Categorize
            if bmi < 18.5:
                category = "underweight"
            elif bmi < 25:
                category = "normal weight"
            elif bmi < 30:
                category = "overweight"
            else:
                category = "obese"

            result = f"BMI: {bmi:.1f} ({category})"

            logger.info(f"BMI calculation: {weight} lbs, {height} in = {bmi:.1f}")
            return result

        except Exception as e:
            logger.error(f"BMI calculation error: {e}")
            return "Couldn't calculate BMI"

    def compound_interest(self, principal, rate, time_years):
        """Calculate compound interest (annual compounding)"""
        try:
            p = float(principal)
            r = float(rate) / 100  # Convert percentage to decimal
            t = float(time_years)

            if p < 0 or r < 0 or t < 0:
                return "Values must be positive"

            # A = P(1 + r)^t
            amount = p * ((1 + r) ** t)
            interest = amount - p

            result = f"After {t} years at {rate}% annual rate: "
            result += f"Total: ${amount:,.2f}, Interest earned: ${interest:,.2f}"

            logger.info(f"Compound interest: ${p} at {rate}% for {t} years = ${amount}")
            return result

        except Exception as e:
            logger.error(f"Compound interest error: {e}")
            return "Couldn't calculate compound interest"
