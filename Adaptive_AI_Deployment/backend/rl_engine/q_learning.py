
import json
import os
import random
import numpy as np

# Path to save Q-Table
Q_TABLE_PATH = os.path.join(os.path.dirname(__file__), "q_table.json")

class QLearningEngine:
    """
    A simple Reinforcement Learning engine (Contextual Bandit) for optimizing recommendations.
    Uses Q-Learning to learn the 'value' of each recommendation action for a given emotional state.
    """

    def __init__(self, actions, learning_rate=0.1, discount_factor=0.9, epsilon=0.2):
        """
        Initialize the RL Engine.
        
        Args:
            actions: List of possible actions (recommendations).
            learning_rate: Alpha - how much new info overrides old info.
            discount_factor: Gamma - importance of future rewards (less relevant for Bandits but kept for standard Q).
            epsilon: Exploration rate - chance of choosing random action.
        """
        self.actions = actions
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        self.q_table = self._load_q_table()

    def _load_q_table(self):
        """Load Q-Table from disk or initialize if missing."""
        if os.path.exists(Q_TABLE_PATH):
            try:
                with open(Q_TABLE_PATH, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading Q-Table: {e}")
        return {}

    def _save_q_table(self):
        """Save Q-Table to disk."""
        try:
            with open(Q_TABLE_PATH, "w") as f:
                json.dump(self.q_table, f, indent=4)
        except Exception as e:
            print(f"Error saving Q-Table: {e}")

    def get_q_value(self, state, action):
        """Get Q-value for a state-action pair."""
        return self.q_table.get(state, {}).get(action, 0.0)

    def choose_action(self, state):
        """
        Choose an action based on Epsilon-Greedy policy.
        
        Args:
            state: current emotional state (e.g., "sad", "happy").
            
        Returns:
            Selected action (recommendation string).
        """
        state = state.lower()
        
        # Ensure state exists in Q-table
        if state not in self.q_table:
            self.q_table[state] = {action: 0.0 for action in self.actions}

        # Exploration: Random action
        if random.random() < self.epsilon:
            return random.choice(self.actions)

        # Exploitation: Best action
        # Get all Q-values for this state
        state_actions = self.q_table[state]
        
        # Find max Q-value
        max_q = max(state_actions.values())
        
        # Get all actions that share the max Q-value (handle ties randomly)
        best_actions = [action for action, q in state_actions.items() if q == max_q]
        
        return random.choice(best_actions)

    def update(self, state, action, reward):
        """
        Update the Q-Table based on feedback.
        
        Args:
            state: The emotion state.
            action: The recommendation given.
            reward: +1 (Thumbs Up) or -1 (Thumbs Down).
        """
        state = state.lower()
        
        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in self.actions}
            
        old_value = self.q_table[state].get(action, 0.0)
        
        # Q-Learning Update Rule (Simplified for Bandit: Q(s,a) = Q(s,a) + alpha * (reward - Q(s,a)))
        # Since there is no "next state" in this simple recsys, we treat it as a 1-step episode.
        new_value = old_value + self.lr * (reward - old_value)
        
        self.q_table[state][action] = new_value
        self._save_q_table()
        
        print(f"[RL] Updated Q-Value for {state} -> {action}: {old_value:.2f} -> {new_value:.2f} (Reward: {reward})")

