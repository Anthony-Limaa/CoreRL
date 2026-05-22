import random

class Agent:
    """
    Representa un agente autónomo dentro del Sistema Multi-Agente.
    Mantiene su propio estado, política (policy) y registro de recompensas (reward).
    """
    def __init__(self, agent_id, priority="media"):
        self.agent_id = agent_id
        self.priority = priority
        
        # Estado propio del agente (Requisito del documento)
        self.status = "disponible"  # Puede ser: disponible, ocupado, mantenimiento
        
        # Registro de recompensas (Requisito del documento)
        self.reward_accumulated = 0
        
        # Política de decisión (Requisito del documento)
        # Se inicializa vacía, pero será guiada por la Red Neuronal (DQN)
        self.policy = None  

    def get_agent_info(self):
        """Devuelve un diccionario con el contexto actual del agente para el motor lógico."""
        return {
            "agent_id": self.agent_id,
            "priority": self.priority,
            "status": self.status
        }

    def decide_action(self, state_data, neuro_engine, dqn_model=None):
        """
        Flujo de decisión principal (Razonamiento Neuro-Simbólico):
        1. La Red Neuronal (DQN) propone una acción basada en el entorno.
        2. El Motor Lógico evalúa si la acción viola alguna regla.
        3. Se ejecuta la acción final.
        """
        # Si el agente está en mantenimiento o ocupado, su "intuición" por defecto es esperar (0)
        if self.status != "disponible":
            proposed_action = 0
        else:
            # 1. Predicción Conexionista (Red Neuronal)
            if dqn_model is not None:
                # Aquí la IA conexionista evalúa el state_data y elige
                proposed_action = dqn_model.predict(state_data)
            else:
                # Si el modelo aún no está entrenado, toma una decisión exploratoria
                # Acciones: 0 (Esperar), 1 (Asignar), 2 (Colaborar)
                proposed_action = random.choice([0, 1, 2])

        # 2. Evaluación Simbólica (Lógica)
        agent_info = self.get_agent_info()
        veto, final_action, rule_triggered = neuro_engine.evaluate_action(
    state_data, self.agent_id, proposed_action
)

        # Actualizamos temporalmente el estado del agente según la acción final
        if final_action == 1:
            self.status = "ocupado"
        elif final_action == 0 and self.status == "ocupado":
            # Simulación simple: si esperó, se libera
            self.status = "disponible"

        return final_action, rule_triggered

    def update_reward(self, reward):
        """Acumula la recompensa recibida tras ejecutar una acción en el entorno."""
        self.reward_accumulated += reward