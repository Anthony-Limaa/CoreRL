# 🧠 CoreRL Suite
**Arquitectura Híbrida de Coordinación Logística Multi-Agente basada en Deep Reinforcement Learning, Meta-Learning y AutoML**

![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)

---

## 📌 Descripción del Proyecto
**CoreRL Suite** es un ecosistema avanzado de Inteligencia Artificial diseñado para resolver problemas de enrutamiento y asignación de recursos logísticos bajo incertidumbre en entornos de misión crítica (específicamente modelado para el municipio de Santa Catarina Mita y sus aldeas periféricas).

Desarrollado como proyecto final de investigación para la clase de **Inteligencia Artificial**, este sistema supera las limitaciones tradicionales de los algoritmos clásicos y las redes neuronales puras (cajas negras) mediante la hibridación de paradigmas computacionales.

### ✨ Características Principales
* **Deep Reinforcement Learning (DQN):** Agentes autónomos que optimizan la distribución mediante la Ecuación de Bellman, *Experience Replay* y *Target Networks*.
* **Motor Neuro-Simbólico:** Un sistema experto con $\ge 15$ reglas lógicas estrictas que audita y veta en milisegundos las decisiones estocásticas de la red neuronal, garantizando operaciones 100% seguras.
* **Meta-Learning Activo:** Algoritmo de auto-regulación sináptica que ajusta el *Learning Rate* de PyTorch dinámicamente al detectar anomalías o colapsos en el entorno ("Tormentas").
* **Automated Machine Learning (AutoML):** Pipeline predictivo apoyado en Pandas y Scikit-Learn que evalúa múltiples modelos de forma cruzada, auto-seleccionando el algoritmo óptimo (ej. Gradient Boosting) para predecir riesgos estadísticos.
* **Dashboard Reactivo:** Telemetría en tiempo real, mapas topológicos interactivos y auditoría matemática de la función de pérdida.

---

## 📸 Interfaz Gráfica (Dashboard)
![CoreRL Dashboard](./docs/dashboard.png)
*(Nota: Para que esta imagen cargue en GitHub, crea una carpeta llamada `docs` en tu proyecto, guarda ahí tu captura de pantalla con el nombre `dashboard.png` y súbela junto con tu código).*

---

## 📂 Estructura del Monorepo

El ecosistema está desacoplado en una arquitectura cliente-servidor dentro de este mismo repositorio:

```text
CoreRL/
├── backend/               # Cerebro neuronal y servidor API
│   ├── core_ia/           # Módulos de PyTorch, AutoML y Motor Lógico
│   ├── data/              # Archivos de memoria (.pth, .pkl, .csv)
│   ├── main.py            # Endpoints de FastAPI
│   └── requirements.txt   # Dependencias de Python
│
├── frontend/              # Interfaz gráfica y telemetría
│   ├── src/               # Componentes de React, Recharts y Tailwind
│   ├── index.html
│   ├── vite.config.js
│   └── package.json       # Dependencias de Node.js
│
├── .gitignore
└── README.md
