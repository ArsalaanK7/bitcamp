from typing import Dict, Any, List
from .base_agent import BaseAgent

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.plan_templates = {
            'high_energy': [
                "30-minute cardio workout",
                "15-minute meditation",
                "Healthy meal planning"
            ],
            'medium_energy': [
                "20-minute yoga session",
                "10-minute breathing exercises",
                "Light stretching"
            ],
            'low_energy': [
                "Gentle walking",
                "Mindful breathing",
                "Rest and recovery"
            ]
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a personalized plan based on user state"""
        energy_level = input_data.get('energy_level', 5)
        mood = input_data.get('mood', 5)
        sleep_hours = input_data.get('sleep_hours', 7)
        
        # Determine energy category
        if energy_level >= 7:
            energy_category = 'high_energy'
        elif energy_level >= 4:
            energy_category = 'medium_energy'
        else:
            energy_category = 'low_energy'
        
        # Get base plan
        plan = self.plan_templates[energy_category].copy()
        
        # Adjust plan based on mood
        if mood < 4:
            plan.insert(0, "5-minute mood boost exercise")
        
        # Adjust plan based on sleep
        if sleep_hours < 6:
            plan.append("Evening relaxation routine")
        
        return {
            'plan': plan,
            'energy_category': energy_category,
            'mood_adjustments': mood < 4,
            'sleep_adjustments': sleep_hours < 6
        }
    
    def get_recommendations(self, mood: int, sleep_hours: float, energy_level: int) -> List[str]:
        """Get personalized recommendations based on user state"""
        result = self.process({
            'mood': mood,
            'sleep_hours': sleep_hours,
            'energy_level': energy_level
        })
        return result['plan'] 