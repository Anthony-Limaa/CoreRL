class NeuroSymbolicEngine:
    def __init__(self):
        # Base de conocimiento (Hechos y umbrales)
        self.UMBRAL_CRITICO_RECURSOS = 15
        self.UMBRAL_ABUNDANCIA = 80
        self.EMERGENCIAS_CATASTROFE = 4

    def evaluate_action(self, state_data, agent_id, proposed_action):
        """
        Actúa como un motor de inferencia. Evalúa la acción de la red neuronal
        contra 15 reglas lógicas estrictas.
        Retorna: (Veto: bool, Accion_Forzada: int, Justificacion: str)
        """
        r = state_data["resources"]
        e = state_data["emergencies"]
        activos = state_data["agents_active"]
        a = proposed_action

        # ==========================================================
        # BASE DE REGLAS (15 AXIOMAS LÓGICOS TIPO PROLOG)
        # ==========================================================

        # --- BLOQUE 1: REGLAS DE SEGURIDAD ABSOLUTA (Prevención de colapso) ---
        # R1: Si no hay emergencias, prohibido gastar recursos.
        if e == 0 and a != 0:
            return True, 0, "R1: Sin crisis. Despliegue vetado."
            
        # R2: Si los recursos están en 0, nadie puede hacer nada.
        if r <= 0 and a != 0:
            return True, 0, "R2: Colapso logístico. Fuerza inacción."
            
        # R3: Si los recursos son críticos (<15) y hay emergencias, se prohíbe el despliegue individual, obligando colaboración.
        if r < self.UMBRAL_CRITICO_RECURSOS and e > 0 and a == 1:
            return True, 2, "R3: Recursos críticos. Forzando colaboración."

        # --- BLOQUE 2: REGLAS DE RESPUESTA A CATASTROFES ---
        # R4: Si es una catástrofe (>=4) y hay recursos, el Agente 1 (Alta prioridad) DEBE asignar.
        if e >= self.EMERGENCIAS_CATASTROFE and r > 20 and agent_id == 1 and a != 1:
            return True, 1, "R4: Catástrofe. Agente Élite forzado a Desplegar."
            
        # R5: En catástrofe, prohibido quedarse monitoreando si hay recursos mínimos.
        if e >= self.EMERGENCIAS_CATASTROFE and r >= 30 and a == 0:
            return True, 1, "R5: Catástrofe activa. Prohibido monitorear."

        # --- BLOQUE 3: REGLAS DE OPTIMIZACIÓN Y BALANCEO ---
        # R6: Si hay abundancia de recursos (>80) y hay emergencias, prohibido quedarse sin hacer nada.
        if r > self.UMBRAL_ABUNDANCIA and e > 0 and a == 0:
            return True, 1, "R6: Abundancia detectada. Despliegue forzado."
            
        # R7: Si solo hay 1 emergencia y ya hay 2 agentes activos, el tercer agente debe quedarse en base.
        if e == 1 and activos >= 2 and a != 0:
            return True, 0, "R7: Emergencia controlada. Conservando nodo."
            
        # R8: Agente 3 (Baja prioridad) no debe gastar recursos si estamos por debajo de 30.
        if agent_id == 3 and r < 30 and a == 1:
            return True, 2, "R8: Nodo menor restringido por escasez."

        # R9: Si un agente propone colaborar (2) pero no hay emergencias, es un error lógico de la red.
        if a == 2 and e == 0:
            return True, 0, "R9: Colaboración ilógica (Cero crisis)."

        # --- BLOQUE 4: REGLAS DE HEURÍSTICA DE ESCENARIOS ESPECÍFICOS ---
        # R10: Si los recursos están exactamente al máximo (100) y hay crisis, priorizar despliegue masivo.
        if r == 100 and e > 0 and a != 1:
            return True, 1, "R10: Inventario lleno. Liberación inmediata."

        # R11: Si hay 2 emergencias y el Agente 2 está monitoreando, forzar su activación de soporte.
        if e == 2 and agent_id == 2 and a == 0 and r > 20:
            return True, 2, "R11: Balanceo intermedio. Agente 2 a soporte."

        # R12: Si nadie está haciendo nada (activos=0) y hay emergencias, el primero que evalúe debe actuar.
        if activos == 0 and e > 0 and a == 0 and r > 10:
            return True, 1, "R12: Sistema inactivo. Activación de vanguardia."

        # R13: Prohibir asignaciones de alto costo si los recursos están entre 15 y 25 (Zona amarilla) para agentes de baja prioridad.
        if 15 <= r <= 25 and agent_id == 3 and a == 1:
            return True, 0, "R13: Zona amarilla. Nodo 3 bloqueado."

        # R14: Si hay 3 emergencias exactas y recursos medios, forzar colaboración para evitar vaciado rápido.
        if e == 3 and 30 < r < 60 and a == 1:
            return True, 2, "R14: Tensión moderada. Forzando eficiencia."

        # R15: Regla de contingencia final (Failsafe)
        if r < 5 and a == 2:
            return True, 0, "R15: Failsafe absoluto. Energía insuficiente."

        # Si el modelo neuronal propuso algo que no viola ninguna regla, se aprueba su decisión.
        return False, a, "Ninguna (Decisión Neuronal pura)"