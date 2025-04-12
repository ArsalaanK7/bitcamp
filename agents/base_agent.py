from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseAgent(ABC):
    def __init__(self):
        self.state = {}
        self.history = []
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return a response"""
        pass
    
    def update_state(self, new_state: Dict[str, Any]):
        """Update the agent's internal state"""
        self.state.update(new_state)
    
    def add_to_history(self, interaction: Dict[str, Any]):
        """Add an interaction to the agent's history"""
        self.history.append(interaction)
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get the agent's interaction history"""
        return self.history 