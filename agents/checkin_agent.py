from typing import Dict, Any, List
from datetime import datetime
from .base_agent import BaseAgent

class CheckinAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.feedback_templates = {
            'high_energy': [
                "Great energy level! Perfect time for physical activity.",
                "Your energy is high - consider tackling challenging tasks.",
                "Excellent energy - make the most of it!"
            ],
            'medium_energy': [
                "Moderate energy - balance activity with rest.",
                "Steady energy level - good for focused work.",
                "Stable energy - maintain your current pace."
            ],
            'low_energy': [
                "Take it easy and focus on recovery.",
                "Consider some gentle movement to boost energy.",
                "Rest and recharge - your body needs it."
            ]
        }
        
        self.mood_responses = {
            'high': [
                "Wonderful mood! Keep the positive energy flowing.",
                "Your positive attitude is inspiring!",
                "Great to see you're feeling good!"
            ],
            'medium': [
                "Stable mood - maintain your balance.",
                "Steady mood - keep up the good work.",
                "Balanced mood - you're doing well."
            ],
            'low': [
                "Remember, it's okay to have off days.",
                "Take care of yourself - you deserve it.",
                "Small steps forward still count as progress."
            ]
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process check-in data and generate appropriate responses"""
        mood = input_data.get('mood', 5)
        energy_level = input_data.get('energy_level', 5)
        sleep_hours = input_data.get('sleep_hours', 7)
        
        # Determine energy category
        if energy_level >= 7:
            energy_category = 'high_energy'
        elif energy_level >= 4:
            energy_category = 'medium_energy'
        else:
            energy_category = 'low_energy'
        
        # Determine mood category
        if mood >= 7:
            mood_category = 'high'
        elif mood >= 4:
            mood_category = 'medium'
        else:
            mood_category = 'low'
        
        # Generate feedback
        energy_feedback = self._get_random_feedback(self.feedback_templates[energy_category])
        mood_feedback = self._get_random_feedback(self.mood_responses[mood_category])
        
        # Generate sleep advice if needed
        sleep_advice = None
        if sleep_hours < 6:
            sleep_advice = "Consider getting more sleep tonight to improve your energy levels."
        elif sleep_hours > 9:
            sleep_advice = "You might want to aim for 7-9 hours of sleep for optimal health."
        
        return {
            'energy_feedback': energy_feedback,
            'mood_feedback': mood_feedback,
            'sleep_advice': sleep_advice,
            'energy_category': energy_category,
            'mood_category': mood_category
        }
    
    def _get_random_feedback(self, templates: List[str]) -> str:
        """Get a random feedback message from the templates"""
        import random
        return random.choice(templates)
    
    def get_checkin_feedback(self, mood: int, energy_level: int, sleep_hours: float) -> Dict[str, str]:
        """Get personalized feedback based on check-in data"""
        result = self.process({
            'mood': mood,
            'energy_level': energy_level,
            'sleep_hours': sleep_hours
        })
        return {
            'energy_feedback': result['energy_feedback'],
            'mood_feedback': result['mood_feedback'],
            'sleep_advice': result['sleep_advice']
        } 