import random

class LogisticsEnvironment:
    def __init__(self, num_agents=3, initial_resources=100):
        self.num_agents = num_agents
        self.total_resources = initial_resources
        self.current_resources = initial_resources
        self.emergencies_active = 0
        
        # El Estado (S) del entorno.
        # Representación: [recursos_restantes, num_emergencias, estado_agente_1, ..., estado_agente_n]
        self.state = self.reset()

    def reset(self):
        """Reinicia el entorno al estado inicial para un nuevo episodio de aprendizaje."""
        self.current_resources = self.total_resources
        self.emergencies_active = 0
        # Estado inicial: Todos los agentes están en estado 0 (Disponibles/En base)
        self.state = [self.current_resources, self.emergencies_active] + [0] * self.num_agents
        return self.state

    def step(self, actions):
        """
        Ejecuta un paso en la simulación basado en las Acciones (A) de los agentes.
        Acciones posibles: 0 (Esperar), 1 (Asignar Recurso), 2 (Colaborar)
        """
        rewards = []
        
        # 1. Simular cambios inesperados en el entorno dinámico
        if random.random() < 0.2:  # 20% de probabilidad de una nueva emergencia
            self.emergencies_active += 1

        # 2. Procesar las acciones de los agentes
        for i, action in enumerate(actions):
            reward = 0
            
            if action == 1 and self.current_resources > 0 and self.emergencies_active > 0:
                # Decisión correcta: Asigna recurso a una emergencia
                self.current_resources -= 10
                self.emergencies_active -= 1
                reward = 10  # Recompensa positiva (R)
            elif action == 1 and (self.current_resources <= 0 or self.emergencies_active == 0):
                # Decisión incorrecta: Intenta gastar recursos sin emergencias o sin saldo
                reward = -5  # Penalización
            elif action == 0 and self.emergencies_active > 0:
                # Fallo crítico: Esperar mientras hay emergencias
                reward = -10 # Penalización crítica
            else:
                # Acción neutral
                reward = -1
                
            rewards.append(reward)

        # Actualizar el estado global
        self.state = [self.current_resources, self.emergencies_active] + list(actions)
        
        # Determinar si el episodio terminó (sin recursos o colapso de emergencias)
        done = self.current_resources <= 0 or self.emergencies_active > 5
        
        return self.state, rewards, done