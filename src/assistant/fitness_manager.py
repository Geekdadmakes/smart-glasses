"""
Fitness & Health Manager - Step counter, workout timer, water reminder, health tracking
"""

import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class FitnessManager:
    """Manage fitness and health features"""

    def __init__(self, data_dir='./fitness'):
        """Initialize fitness manager"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.fitness_file = self.data_dir / 'fitness_data.json'
        self.water_file = self.data_dir / 'water_log.json'

        # Load data
        self.fitness_data = self._load_json(self.fitness_file, {
            'daily_step_goal': 10000,
            'water_goal_oz': 64,
            'workout_history': []
        })

        self.water_log = self._load_json(self.water_file, [])

        # Workout timer state
        self.workout_start_time = None
        self.workout_type = None

        logger.info("Fitness Manager initialized")

    def _load_json(self, file_path, default):
        """Load JSON file"""
        try:
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
        return default

    def _save_json(self, file_path, data):
        """Save JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving {file_path}: {e}")

    def start_workout(self, workout_type='workout'):
        """Start workout timer"""
        self.workout_start_time = time.time()
        self.workout_type = workout_type

        logger.info(f"Workout started: {workout_type}")
        return f"{workout_type.capitalize()} timer started"

    def end_workout(self):
        """End workout timer and record"""
        if not self.workout_start_time:
            return "No workout in progress"

        duration_seconds = int(time.time() - self.workout_start_time)
        duration_minutes = duration_seconds // 60

        # Record workout
        workout_record = {
            'type': self.workout_type or 'workout',
            'date': datetime.now().isoformat(),
            'duration_seconds': duration_seconds,
            'duration_minutes': duration_minutes
        }

        self.fitness_data['workout_history'].append(workout_record)
        self._save_json(self.fitness_file, self.fitness_data)

        result = f"{self.workout_type.capitalize()} completed! Duration: {duration_minutes} minutes"

        # Reset
        self.workout_start_time = None
        self.workout_type = None

        logger.info(f"Workout ended: {duration_minutes} minutes")
        return result

    def get_workout_status(self):
        """Get current workout status"""
        if not self.workout_start_time:
            return "No workout in progress"

        elapsed = int(time.time() - self.workout_start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60

        result = f"{self.workout_type.capitalize()} in progress: {minutes} minutes, {seconds} seconds"
        logger.info(result)
        return result

    def log_water(self, ounces):
        """Log water intake"""
        try:
            ounces = float(ounces)

            log_entry = {
                'date': datetime.now().isoformat(),
                'ounces': ounces
            }

            self.water_log.append(log_entry)
            self._save_json(self.water_file, self.water_log)

            # Calculate today's total
            today_total = self.get_today_water_total()

            result = f"Logged {ounces} oz of water. Today's total: {today_total} oz"

            # Check if goal reached
            goal = self.fitness_data.get('water_goal_oz', 64)
            if today_total >= goal:
                result += f". Congratulations, you've reached your daily goal of {goal} oz!"

            logger.info(f"Water logged: {ounces} oz")
            return result

        except Exception as e:
            logger.error(f"Water log error: {e}")
            return "Couldn't log water intake"

    def get_today_water_total(self):
        """Get total water for today"""
        today = datetime.now().date()

        total = 0
        for entry in self.water_log:
            entry_date = datetime.fromisoformat(entry['date']).date()
            if entry_date == today:
                total += entry.get('ounces', 0)

        return total

    def get_water_status(self):
        """Get water intake status"""
        today_total = self.get_today_water_total()
        goal = self.fitness_data.get('water_goal_oz', 64)

        remaining = max(0, goal - today_total)

        result = f"Water today: {today_total} oz out of {goal} oz goal"
        if remaining > 0:
            result += f". {remaining} oz remaining"
        else:
            result += ". Goal reached!"

        logger.info(result)
        return result

    def set_water_goal(self, ounces):
        """Set daily water goal"""
        try:
            ounces = float(ounces)
            self.fitness_data['water_goal_oz'] = ounces
            self._save_json(self.fitness_file, self.fitness_data)

            logger.info(f"Water goal set: {ounces} oz")
            return f"Daily water goal set to {ounces} ounces"

        except Exception as e:
            logger.error(f"Set water goal error: {e}")
            return "Couldn't set water goal"

    def water_reminder(self):
        """Get water reminder message"""
        today_total = self.get_today_water_total()
        goal = self.fitness_data.get('water_goal_oz', 64)

        if today_total >= goal:
            return "Great job! You've reached your water goal for today"

        # Suggest amount
        remaining = goal - today_total
        suggestion = min(remaining, 16)  # Suggest up to 16 oz at a time

        result = f"Time to hydrate! You've had {today_total} oz today. "
        result += f"Try drinking {suggestion} oz now"

        logger.info("Water reminder sent")
        return result

    def get_workout_summary(self, days=7):
        """Get workout summary for past N days"""
        cutoff_date = datetime.now() - timedelta(days=days)

        recent_workouts = [
            w for w in self.fitness_data.get('workout_history', [])
            if datetime.fromisoformat(w['date']) > cutoff_date
        ]

        if not recent_workouts:
            return f"No workouts recorded in the past {days} days"

        total_minutes = sum(w['duration_minutes'] for w in recent_workouts)
        count = len(recent_workouts)

        result = f"Past {days} days: {count} workouts, {total_minutes} total minutes. "
        result += f"Average: {total_minutes // count if count > 0 else 0} minutes per workout"

        logger.info(f"Workout summary: {count} workouts, {total_minutes} min")
        return result

    def heart_rate_zone(self, age, heart_rate):
        """Calculate heart rate zone"""
        try:
            age = int(age)
            hr = int(heart_rate)

            # Calculate max heart rate (220 - age)
            max_hr = 220 - age

            # Calculate zones
            zones = {
                'resting': (0, max_hr * 0.50),
                'warm_up': (max_hr * 0.50, max_hr * 0.60),
                'fat_burn': (max_hr * 0.60, max_hr * 0.70),
                'cardio': (max_hr * 0.70, max_hr * 0.85),
                'peak': (max_hr * 0.85, max_hr)
            }

            # Determine zone
            current_zone = 'above max'
            for zone_name, (low, high) in zones.items():
                if low <= hr < high:
                    current_zone = zone_name
                    break

            result = f"Heart rate {hr} bpm. Zone: {current_zone}. Max HR: {max_hr} bpm"

            logger.info(f"HR zone: {current_zone} ({hr} bpm)")
            return result

        except Exception as e:
            logger.error(f"Heart rate zone error: {e}")
            return "Couldn't calculate heart rate zone"

    def calories_burned(self, activity, duration_minutes, weight_lbs):
        """Estimate calories burned (rough estimates)"""
        try:
            duration = float(duration_minutes)
            weight = float(weight_lbs)

            # MET values (Metabolic Equivalent of Task)
            met_values = {
                'walking': 3.5,
                'running': 9.0,
                'cycling': 7.0,
                'swimming': 8.0,
                'yoga': 3.0,
                'strength': 5.0,
                'hiit': 10.0,
                'dancing': 5.5,
                'basketball': 8.0,
                'soccer': 10.0
            }

            activity_lower = activity.lower()
            met = met_values.get(activity_lower, 5.0)  # Default to moderate

            # Calories = MET * weight(kg) * duration(hours)
            weight_kg = weight * 0.453592
            duration_hours = duration / 60

            calories = met * weight_kg * duration_hours

            result = f"{activity.capitalize()} for {duration:.0f} minutes burns approximately {calories:.0f} calories"

            logger.info(f"Calories: {activity} = {calories:.0f} cal")
            return result

        except Exception as e:
            logger.error(f"Calories calculation error: {e}")
            return "Couldn't calculate calories"
