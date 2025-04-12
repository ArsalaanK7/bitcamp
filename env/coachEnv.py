# env/neura_coach_env.py
import gym
from gym import spaces
import numpy as np

class NeuraCoachEnv(gym.Env):
    """
    Custom Environment for NeuraCoach where the state includes:
        - Mood (normalized score)
        - Physical activity level (minutes of exercise)
        - Sleep hours (normalized)
        - Journaling status (binary: 0 or 1)
    """
    def __init__(self):
        super(NeuraCoachEnv, self).__init__()
        # Define state space (e.g., a vector with 4 values)
        self.observation_space = spaces.Box(low=0, high=1, shape=(4,), dtype=np.float32)
        # Define action space: 0 = no action, 1 = suggest exercise, 2 = suggest mindfulness, 3 = suggest sleep tip, etc.
        self.action_space = spaces.Discrete(4)
        self.state = np.random.rand(4)
        self.done = False

    def reset(self):
        self.state = np.random.rand(4)
        self.done = False
        return self.state

    def step(self, action):
        # Implement how the state changes based on action.
        # This is a simplified example; in practice, use a more elaborate model.
        # Simulate state update
        self.state = np.random.rand(4)
        # Compute reward:
        # Suppose reward is higher when action aligns with an "ideal" behavior suggested by the state.
        reward = 1.0 if action == int(np.argmax(self.state)) else 0.5
        # A simple rule to finish episode (for instance, after one day cycle)
        self.done = np.random.rand() > 0.95  # Random termination for simulation
        return self.state, reward, self.done, {}

    def render(self, mode='human'):
        print(f"Current state: {self.state}")
