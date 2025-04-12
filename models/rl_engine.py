import numpy as np
from typing import Dict, List, Tuple
import gym
from gym import spaces

class WellnessEnv(gym.Env):
    def __init__(self):
        super().__init__()
        
        # Define action space (different types of recommendations)
        self.action_space = spaces.Discrete(5)  # 5 different recommendation types
        
        # Define observation space (user state)
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0]),  # mood, energy, sleep
            high=np.array([10, 10, 12]),
            dtype=np.float32
        )
        
        self.state = None
        self.reset()
    
    def reset(self):
        self.state = np.array([5.0, 5.0, 7.0])  # Initial state
        return self.state
    
    def step(self, action):
        # Simulate environment response
        reward = 0
        done = False
        
        # Different actions have different effects
        if action == 0:  # Physical activity
            reward = 2 if self.state[1] > 5 else 1
        elif action == 1:  # Meditation
            reward = 2 if self.state[0] < 5 else 1
        elif action == 2:  # Sleep improvement
            reward = 2 if self.state[2] < 7 else 1
        elif action == 3:  # Social activity
            reward = 2 if self.state[0] < 6 else 1
        else:  # Rest
            reward = 2 if self.state[1] < 4 else 1
        
        # Update state (simplified)
        self.state += np.random.normal(0, 0.5, 3)
        self.state = np.clip(self.state, 0, 10)
        
        return self.state, reward, done, {}

class RLEngine:
    def __init__(self):
        self.env = WellnessEnv()
        self.q_table = {}
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.1
    
    def _get_state_key(self, state: np.ndarray) -> str:
        """Convert state array to string key for Q-table"""
        return ','.join(map(str, state.round(1)))
    
    def _get_action(self, state: np.ndarray) -> int:
        """Choose action using epsilon-greedy policy"""
        state_key = self._get_state_key(state)
        
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(5)
        
        if np.random.random() < self.epsilon:
            return np.random.randint(5)
        return np.argmax(self.q_table[state_key])
    
    def update(self, activity: str, mood: int):
        """Update Q-values based on user activity and mood"""
        state = self.env.state
        state_key = self._get_state_key(state)
        
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(5)
        
        # Map activity to action index
        action_map = {
            'workout': 0,
            'meditation': 1,
            'sleep': 2,
            'social': 3,
            'rest': 4
        }
        
        action = action_map.get(activity.lower(), 0)
        
        # Get next state and reward
        next_state, reward, _, _ = self.env.step(action)
        next_state_key = self._get_state_key(next_state)
        
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = np.zeros(5)
        
        # Update Q-value
        current_q = self.q_table[state_key][action]
        next_max_q = np.max(self.q_table[next_state_key])
        
        # Q-learning update
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * next_max_q - current_q
        )
        self.q_table[state_key][action] = new_q
    
    def get_best_action(self, state: np.ndarray) -> Tuple[int, float]:
        """Get the best action for the current state"""
        state_key = self._get_state_key(state)
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(5)
        return np.argmax(self.q_table[state_key]), np.max(self.q_table[state_key]) 