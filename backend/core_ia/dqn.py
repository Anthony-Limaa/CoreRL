import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque
import numpy as np
import os

class DQNNetwork(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQNNetwork, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, output_dim)
        )
    def forward(self, x):
        return self.net(x)

class DQNAgent:
    def __init__(self, state_dim, action_dim, lr=0.001, gamma=0.99, epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.01):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma                
        self.epsilon = epsilon            
        self.epsilon_decay = epsilon_decay 
        self.epsilon_min = epsilon_min     
        
        self.model = DQNNetwork(state_dim, action_dim)
        self.target_model = DQNNetwork(state_dim, action_dim) 
        self.update_target_network()

        # --- OPTIMIZACIÓN AVANZADA Y META-LEARNING ---
        self.base_lr = lr
        self.current_lr = lr
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.current_lr)
        self.criterion = nn.MSELoss()
        
        # Memoria del error para que la IA se evalúe a sí misma
        self.loss_history = deque(maxlen=10) 

        self.memory = deque(maxlen=2000)
        self.batch_size = 32 
        self.model_path = "data/cerebro_dqn.pth"

    def update_target_network(self):
        self.target_model.load_state_dict(self.model.state_dict())

    def save_model(self):
        os.makedirs("data", exist_ok=True)
        torch.save(self.model.state_dict(), self.model_path)

    def load_model(self):
        if os.path.exists(self.model_path):
            self.model.load_state_dict(torch.load(self.model_path))
            self.update_target_network()
            self.epsilon = self.epsilon_min
            return True
        return False

    def predict(self, state_vector):
        if random.random() <= self.epsilon:
            return random.randint(0, self.action_dim - 1)
        
        if isinstance(state_vector, dict):
            state_vector = state_vector.get("vector_pytorch", [0]*self.state_dim)
        state_vector = [float(x) for x in state_vector]
        
        state_tensor = torch.FloatTensor(state_vector).unsqueeze(0)
        with torch.no_grad():
            q_values = self.model(state_tensor)
        return torch.argmax(q_values).item()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def meta_learning_step(self):
        """
        APRENDER A APRENDER: Ajusta dinámicamente el Learning Rate.
        Si hay un pico de error (caos/tormenta), acelera el aprendizaje.
        Si hay paz, reduce el LR para un ajuste fino.
        """
        if len(self.loss_history) < 10:
            return self.current_lr
            
        recent_loss_avg = sum(self.loss_history) / 10
        
        # Si el error es muy alto (>5.0), significa que el entorno cambió drásticamente
        if recent_loss_avg > 5.0:
            self.current_lr = min(self.base_lr * 5, 0.01) # Aceleramos x5
        # Si el error es muy bajo (<1.0), hacemos sintonía fina
        elif recent_loss_avg < 1.0:
            self.current_lr = max(self.base_lr / 5, 0.0001) # Reducimos x5
        else:
            self.current_lr = self.base_lr # Volvemos a la normalidad
            
        # Inyectamos el nuevo Learning Rate al optimizador de PyTorch
        for param_group in self.optimizer.param_groups:
            param_group['lr'] = self.current_lr
            
        return self.current_lr

    def train_step(self):
        if len(self.memory) < self.batch_size:
            return 0.0

        minibatch = random.sample(self.memory, self.batch_size)
        states = torch.FloatTensor(np.array([m[0] for m in minibatch]))
        actions = torch.LongTensor(np.array([m[1] for m in minibatch])).unsqueeze(1)
        rewards = torch.FloatTensor(np.array([m[2] for m in minibatch]))
        next_states = torch.FloatTensor(np.array([m[3] for m in minibatch]))
        dones = torch.FloatTensor(np.array([float(m[4]) for m in minibatch]))

        q_values = self.model(states).gather(1, actions).squeeze(1)

        with torch.no_grad():
            max_next_q_values = self.target_model(next_states).max(1)[0]
            target_q_values = rewards + (self.gamma * max_next_q_values * (1 - dones))

        loss = self.criterion(q_values, target_q_values)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Guardamos el error para el Meta-learning
        loss_val = loss.item()
        self.loss_history.append(loss_val)
        
        # Ejecutamos la meta-optimización
        self.meta_learning_step()

        return loss_val

    def decay_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay