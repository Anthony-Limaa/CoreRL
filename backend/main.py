from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pandas as pd
import os

from core_ia.environment import LogisticsEnvironment
from core_ia.agent import Agent
from core_ia.neuro_symbolic import NeuroSymbolicEngine
from core_ia.dqn import DQNAgent
from core_ia.predictive_ml import EmergencyPredictor

app = FastAPI(title="CoreRL API", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

env = LogisticsEnvironment(num_agents=3, initial_resources=100)
neuro_engine = NeuroSymbolicEngine()
dqn_model = DQNAgent(state_dim=5, action_dim=3)
ml_predictor = EmergencyPredictor()

dqn_loaded = dqn_model.load_model()
ml_predictor.load_model()

agentes = [Agent(agent_id=1, priority="alta"), Agent(agent_id=2, priority="media"), Agent(agent_id=3, priority="baja")]
episodio_actual = 0
LOG_FILE = "data/logs.csv"

def guardar_log_pandas(episodio, recursos, emergencias, acciones, recompensas, reglas):
    data = {"Episodio": [episodio], "Recursos_Restantes": [recursos], "Emergencias_Activas": [emergencias], "Accion_Agente1": [acciones[0]], "Accion_Agente2": [acciones[1]], "Accion_Agente3": [acciones[2]], "Recompensa_Global": [sum(recompensas)], "Intervenciones_Logicas": [" | ".join(reglas)]}
    df = pd.DataFrame(data)
    if not os.path.isfile(LOG_FILE): df.to_csv(LOG_FILE, index=False)
    else: df.to_csv(LOG_FILE, mode='a', header=False, index=False)

@app.get("/")
async def root(): return {"status": "online"}

@app.get("/api/force_chaos")
async def force_chaos():
    env.state[1] = 5
    env.state[0] = max(10, env.state[0] - 30) 
    return {"message": "Desastre inducido"}

@app.get("/api/simulate")
async def simulate_step():
    global episodio_actual
    episodio_actual += 1
    
    current_state = list(env.state)
    current_state_vector = [current_state[0], current_state[1]] + [1 if a.status == "ocupado" else 0 for a in agentes]

    state_data = {
        "resources": current_state[0],
        "emergencies": current_state[1],
        "agents_active": sum(1 for a in agentes if a.status == "ocupado"),
        "vector_pytorch": current_state_vector  
    }

    acciones_tomadas = []
    reglas_activadas = []

    for agente in agentes:
        veto, final_action, regla = neuro_engine.evaluate_action(state_data, agente.agent_id, 0) # Inicializa consulta estricta
        accion_neuronal = dqn_model.predict(current_state_vector)
        veto, final_action, regla = neuro_engine.evaluate_action(state_data, agente.agent_id, accion_neuronal)
        
        acciones_tomadas.append(final_action)
        reglas_activadas.append(f"Ag{agente.agent_id}: {regla}")

    next_state, rewards, done = env.step(acciones_tomadas)
    next_state_vector = [next_state[0], next_state[1]] + [1 if a.status == "ocupado" else 0 for a in agentes]

    loss_value = 0
    for i, agente in enumerate(agentes):
        agente.update_reward(rewards[i])
        dqn_model.remember(state=current_state_vector, action=acciones_tomadas[i], reward=rewards[i], next_state=next_state_vector, done=done)

    loss_value = dqn_model.train_step()
    dqn_model.decay_epsilon()

    if episodio_actual % 10 == 0:
        dqn_model.update_target_network()
        dqn_model.save_model()

    guardar_log_pandas(episodio_actual, next_state[0], next_state[1], acciones_tomadas, rewards, reglas_activadas)

    # --- TRANSMISIÓN DE COMPONENTES DE AUTOML ---
    ml_predictor.train()
    riesgo_futuro, metrics_dict = ml_predictor.predict_risk(next_state[0], next_state[1])

    return {
      "episodio": episodio_actual,
        "estado_actual": {"recursos": next_state[0], "emergencias_activas": next_state[1]},
        "acciones_ejecutadas": acciones_tomadas,
        "recompensas_obtenidas": rewards,
        "intervencion_logica": reglas_activadas,
        "prediccion_riesgo": riesgo_futuro,
        "ml_metrics": metrics_dict,  
        "loss_neuronal": loss_value,
        "cerebro_cargado": dqn_loaded,
        "tasa_exploracion": dqn_model.epsilon,
        "meta_learning_rate": dqn_model.current_lr, # <--- AÑADE ESTA LÍNEA AQUÍ
        "simulacion_terminada": done
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)