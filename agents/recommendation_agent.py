from typing import Dict, Any, List
import numpy as np
from .base_agent import BaseAgent
from models.rl_engine import RLEngine

class RecommendationAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.rl_engine = RLEngine()
        self.recommendation_templates = {
            0: [  # Physical activity
                "30-minute cardio workout",
                "20-minute strength training",
                "15-minute HIIT session"
            ],
            1: [  # Meditation
                "10-minute mindfulness meditation",
                "5-minute breathing exercises",
                "Guided meditation session"
            ],
            2: [  # Sleep improvement
                "Evening relaxation routine",
                "Sleep hygiene checklist",
                "Bedtime wind-down ritual"
            ],
            3: [  # Social activity
                "Connect with a friend",
                "Join a group activity",
                "Share your progress"
            ],
            4: [  # Rest
                "Take a short nap",
                "Do some gentle stretching",
                "Practice self-care"
            ]
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process user state and generate recommendations"""
        mood = input_data.get('mood', 5)
        sleep_hours = input_data.get('sleep_hours', 7)
        energy_level = input_data.get('energy_level', 5)
        
        # Create state array for RL engine
        state = np.array([mood, energy_level, sleep_hours])
        
        # Get best action from RL engine
        action, confidence = self.rl_engine.get_best_action(state)
        
        # Initialize recommendations list
        recommendations = []
        
        # Add primary recommendation from the RL-selected action
        primary_recommendation = np.random.choice(self.recommendation_templates[action])
        recommendations.append(primary_recommendation)
        
        # Add contextual recommendations based on user state
        if mood < 4:
            recommendations.append("5-minute mood boost exercise")
        if sleep_hours < 6:
            recommendations.append("Evening relaxation routine")
        
        # Add one recommendation from each of two other random categories
        other_actions = [i for i in range(5) if i != action]
        selected_actions = np.random.choice(other_actions, size=min(2, len(other_actions)), replace=False)
        
        for secondary_action in selected_actions:
            secondary_recommendation = np.random.choice(self.recommendation_templates[secondary_action])
            recommendations.append(secondary_recommendation)
        
        return {
            'recommendations': recommendations,
            'action': action,
            'confidence': confidence
        }
    
    def get_recommendations(self, mood: int, sleep_hours: float, energy_level: int) -> List[str]:
        """Get personalized recommendations based on user state"""
        result = self.process({
            'mood': mood,
            'sleep_hours': sleep_hours,
            'energy_level': energy_level
        })
        return result['recommendations'] 