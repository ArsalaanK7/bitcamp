# models/q_agent.py
import numpy as np
import random

class QLearningAgent:
    def __init__(self, state_size, action_size, learning_rate=0.1, gamma=0.95, epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.01):
        self.state_size = state_size
        self.action_size = action_size
        self.q_table = np.zeros((state_size, action_size))
        self.lr = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min

    def choose_action(self, state):
        if np.random.rand() < self.epsilon:
            return random.randrange(self.action_size)
        # For simplicity, use discrete state indexing (this is a placeholder strategy)
        state_idx = int(sum(state) * 10) % self.state_size  
        return np.argmax(self.q_table[state_idx])

    def learn(self, state, action, reward, next_state, done):
        state_idx = int(sum(state) * 10) % self.state_size
        next_state_idx = int(sum(next_state) * 10) % self.state_size
        target = reward + self.gamma * np.max(self.q_table[next_state_idx]) * (1 - done)
        self.q_table[state_idx, action] += self.lr * (target - self.q_table[state_idx, action])
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
