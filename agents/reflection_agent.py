from typing import Dict, Any, List
from datetime import datetime, timedelta
from .base_agent import BaseAgent

class ReflectionAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.insight_templates = {
            'positive': [
                "Great progress! You've been consistently {}",
                "Your dedication to {} is impressive",
                "You're making excellent strides in {}",
                "We see you doing grade with {}. Keep it up!",
                "Be proud of yourself for {}"
            ],
            'neutral': [
                "You're maintaining a steady routine with {}",
                "Your commitment to {} is showing results",
                "Keep up the good work with {}",
                "Go you!",
                "You're doing great!"
            ],
            'improvement': [
                "Consider focusing more on {}",
                "There's room for growth in {}",
                "You might benefit from more {}",
                "You're doing great, but you could improve in {}",
                "Try to do more {}. Keep it up!"
            ]
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user data and generate insights"""
        mood_history = input_data.get('mood_history', [])
        activity_history = input_data.get('activity_history', [])
        sleep_history = input_data.get('sleep_history', [])
        
        # Calculate trends
        mood_trend = self._calculate_trend([entry['mood'] for entry in mood_history])
        activity_frequency = self._calculate_activity_frequency(activity_history)
        sleep_trend = self._calculate_trend([entry['sleep'] for entry in sleep_history])
        
        # Generate insights
        insights = []
        
        # Mood insights
        if mood_trend > 0:
            insights.append(self._get_random_insight('positive', 'maintaining a positive mood'))
        elif mood_trend < 0:
            insights.append(self._get_random_insight('improvement', 'mood management'))
        
        # Activity insights
        if activity_frequency >= 0.7:
            insights.append(self._get_random_insight('positive', 'staying active'))
        elif activity_frequency < 0.3:
            insights.append(self._get_random_insight('improvement', 'physical activity'))
        
        # Sleep insights
        if sleep_trend > 0:
            insights.append(self._get_random_insight('positive', 'improving sleep habits'))
        elif sleep_trend < 0:
            insights.append(self._get_random_insight('improvement', 'sleep quality'))
        
        return {
            'insights': insights,
            'mood_trend': mood_trend,
            'activity_frequency': activity_frequency,
            'sleep_trend': sleep_trend
        }
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate the trend of a series of values"""
        if not values or len(values) < 2:
            return 0
        return sum(b - a for a, b in zip(values[:-1], values[1:])) / (len(values) - 1)
    
    def _calculate_activity_frequency(self, activity_history: List[Dict[str, Any]]) -> float:
        """Calculate how often the user completes activities"""
        if not activity_history:
            return 0
        
        # Get activities from the last 7 days
        week_ago = datetime.now() - timedelta(days=7)
        recent_activities = [
            activity for activity in activity_history
            if activity['timestamp'] > week_ago
        ]
        
        return len(recent_activities) / 7  # Normalize to 0-1 range
    
    def _get_random_insight(self, category: str, activity: str) -> str:
        """Get a random insight from the specified category"""
        import random
        template = random.choice(self.insight_templates[category])
        return template.format(activity)
    
    def get_insights(self, mood_history: List[Dict[str, Any]], 
                    activity_history: List[Dict[str, Any]], 
                    sleep_history: List[Dict[str, Any]]) -> List[str]:
        """Get personalized insights based on user history"""
        result = self.process({
            'mood_history': mood_history,
            'activity_history': activity_history,
            'sleep_history': sleep_history
        })
        return result['insights'] 