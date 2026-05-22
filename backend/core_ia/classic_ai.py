class GreedyAgent:
    """
    Agente basado en IA Clásica (Algoritmo Greedy / Búsqueda Local).
    Toma decisiones buscando maximizar la recompensa inmediata basándose en 
    heurísticas estáticas, sin capacidad de aprender del futuro ni del entorno.
    """
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.status = "disponible"
        self.reward_accumulated = 0

    def decide_action(self, state_data):
        """
        Lógica Greedy (Heurística Reactiva):
        - Evalúa el estado actual.
        - Toma la acción que parece más obvia para ganar puntos de inmediato.
        """
        resources = state_data.get("resources", 0)
        emergencies = state_data.get("emergencies", 0)

        # Si no está disponible, la única acción lógica es esperar
        if self.status != "disponible":
            return 0

        # Heurística 1: Si hay emergencias y recursos, ATACAR INMEDIATAMENTE (Acción 1)
        if emergencies > 0 and resources > 0:
            action = 1
            
        # Heurística 2: Si el sistema está colapsando (muchas emergencias, pocos recursos), COLABORAR (Acción 2)
        elif emergencies >= 3 and resources <= 30:
            action = 2
            
        # Heurística 3: Si todo está tranquilo, ESPERAR (Acción 0)
        else:
            action = 0

        # Actualizar estado local simulado
        if action == 1:
            self.status = "ocupado"
        elif action == 0 and self.status == "ocupado":
            self.status = "disponible"

        return action

    def update_reward(self, reward):
        self.reward_accumulated += reward