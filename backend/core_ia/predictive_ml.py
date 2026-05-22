import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import os
import pickle
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

class EmergencyPredictor:
    def __init__(self, log_path="data/logs.csv"):
        self.log_path = log_path
        self.model_path = "data/predictor_ml.pkl"
        self.model = None
        self.is_trained = False
        
        # --- MÉTRICAS EXIGIDAS POR LA NUEVA RÚBRICA DE EVALUACIÓN Y PANDAS ---
        self.metrics = {
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "best_model_name": "Ninguno"
        }

    def load_model(self):
        """Carga el modelo y sus métricas históricas del disco."""
        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as f:
                data = pickle.load(f)
                self.model = data["model"]
                self.metrics = data["metrics"]
            self.is_trained = True
            return True
        return False

    def train(self):
        if not os.path.exists(self.log_path):
            return False
        
        df = pd.read_csv(self.log_path)
        # Necesitamos mínimo 20 filas en Pandas para entrenar el pipeline de AutoML de forma cruzada
        if len(df) < 20: 
            return False

        # Ingeniería de características
        X = df[['Recursos_Restantes', 'Emergencias_Activas']].iloc[:-1] 
        y_futuro = df['Emergencias_Activas'].iloc[1:] 
        y = (y_futuro > 0).astype(int)

        # Validación de balanceo de clases mínimo
        if len(np.unique(y)) < 2:
            return False

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # --- PIPELINE DE AUTOML (Selección y optimización automatizada) ---
        candidate_models = {
            "Random Forest": (RandomForestClassifier(random_state=42), {
                'n_estimators': [10, 30, 50],
                'max_depth': [None, 5, 10]
            }),
            "Gradient Boosting": (GradientBoostingClassifier(random_state=42), {
                'n_estimators': [10, 30, 50],
                'learning_rate': [0.1, 0.2]
            }),
            "Logistic Regression": (LogisticRegression(max_iter=1000), {
                'C': [0.1, 1.0, 10.0]
            })
        }

        best_score = -1
        best_model = None
        best_name = ""

        # El motor de AutoML itera de forma autónoma buscando el mejor algoritmo e hiperparámetros
        for name, (model_obj, params) in candidate_models.items():
            grid = GridSearchCV(model_obj, params, cv=2, scoring='accuracy')
            grid.fit(X_train, y_train)
            
            if grid.best_score_ > best_score:
                best_score = grid.best_score_
                best_model = grid.best_estimator_
                best_name = name

        # Asignamos el modelo ganador
        self.model = best_model
        self.model.fit(X_train, y_train)

        # --- EVALUACIÓN DE ALTO NIVEL ---
        y_pred = self.model.predict(X_test)
        
        self.metrics["accuracy"] = accuracy_score(y_test, y_pred) * 100
        self.metrics["precision"] = precision_score(y_test, y_pred, zero_division=0) * 100
        self.metrics["recall"] = recall_score(y_test, y_pred, zero_division=0) * 100
        self.metrics["f1_score"] = f1_score(y_test, y_pred, zero_division=0) * 100
        self.metrics["best_model_name"] = best_name

        self.is_trained = True
        
        # Persistencia en disco
        os.makedirs("data", exist_ok=True)
        with open(self.model_path, "wb") as f:
            pickle.dump({"model": self.model, "metrics": self.metrics}, f)

        return True

    def predict_risk(self, current_resources, current_emergencies):
        if not self.is_trained or self.model is None:
            return "Ejecutando AutoML...", self.metrics
        
        probabilidades = self.model.predict_proba([[current_resources, current_emergencies]])[0]
        riesgo_porcentaje = probabilidades[1] * 100 if len(probabilidades) > 1 else probabilidades[0] * 100
        
        return f"{riesgo_porcentaje:.1f}%", self.metrics