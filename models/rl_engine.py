import numpy as np
from typing import Dict, List, Tuple
import gym
from gym import spaces

class WellnessEnv(gym.Env):
    def __init__(self):
        super().__init__()
        
        # Define action space (different types of tasks)
        self.action_space = spaces.Discrete(6)  # 6 different task types
        self.action_types = {
            0: "physical",      # Physical activity
            1: "mental",        # Mental/cognitive tasks
            2: "social",        # Social activities
            3: "creative",      # Creative tasks
            4: "relaxation",    # Relaxation activities
            5: "productive"     # Productive tasks
        }
        
        # Define observation space (user state)
        self.observation_space = spaces.Box(
            low=np.array([0, 0]),  # mood, energy
            high=np.array([10, 10]),
            dtype=np.float32
        )
        
        self.state = None
        self.reset()
    
    def reset(self):
        self.state = np.array([5.0, 5.0])  # Initial state (mood, energy)
        return self.state
    
    def step(self, action, mood_change, energy_change):
        # Update state based on actual changes
        new_mood = np.clip(self.state[0] + mood_change, 0, 10)
        new_energy = np.clip(self.state[1] + energy_change, 0, 10)
        
        # Calculate reward based on improvements
        mood_reward = 2 if mood_change > 0 else -1
        energy_reward = 2 if energy_change > 0 else -1
        
        # Different task types have different base rewards
        task_rewards = {
            0: 1.5,  # Physical tasks generally good for energy
            1: 1.0,  # Mental tasks can be draining
            2: 1.8,  # Social activities good for mood
            3: 1.3,  # Creative tasks good for both
            4: 1.6,  # Relaxation good for both
            5: 1.2   # Productive tasks can be draining
        }
        
        # Calculate total reward
        reward = mood_reward + energy_reward + task_rewards[action]
        
        # Update state
        self.state = np.array([new_mood, new_energy])
        
        return self.state, reward, False, {}

class RLEngine:
    def __init__(self):
        self.env = WellnessEnv()
        self.q_table = {}
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.2  # Increased exploration rate
    
    def _get_state_key(self, state: np.ndarray) -> str:
        """Convert state array to string key for Q-table"""
        return ','.join(map(str, state.round(1)))
    
    def _get_action(self, state: np.ndarray) -> Tuple[int, str]:
        """Choose action using epsilon-greedy policy"""
        state_key = self._get_state_key(state)
        
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(6)
        
        if np.random.random() < self.epsilon:
            action = np.random.randint(6)
        else:
            action = np.argmax(self.q_table[state_key])
        
        return action, self.env.action_types[action]
    
    def update(self, task_type: str, mood_change: float, energy_change: float):
        """Update Q-values based on task completion and its effects"""
        state = self.env.state
        state_key = self._get_state_key(state)
        
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(6)
        
        # Map task type to action index
        action_map = {v: k for k, v in self.env.action_types.items()}
        action = action_map.get(task_type.lower(), 0)
        
        # Get next state and reward
        next_state, reward, _, _ = self.env.step(action, mood_change, energy_change)
        next_state_key = self._get_state_key(next_state)
        
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = np.zeros(6)
        
        # Update Q-value
        current_q = self.q_table[state_key][action]
        next_max_q = np.max(self.q_table[next_state_key])
        
        # Q-learning update
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * next_max_q - current_q
        )
        self.q_table[state_key][action] = new_q
        
        # Update environment state
        self.env.state = next_state
    
    def get_best_task_type(self, current_mood: float, current_energy: float) -> str:
        """Get the best task type for the current state"""
        state = np.array([current_mood, current_energy])
        _, task_type = self._get_action(state)
        return task_type 