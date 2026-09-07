import os
from google.adk.agents import Agent

# 1. Agente especializado en respuestas rápidas y concisas
FastTrackAgent = Agent(
    name="FastTrackAgent",
    model="gemini-3.5-flash",
    instruction=(
        "Eres un asistente rápido. Responde consultas generales, saludos o "
        "preguntas simples de manera muy concisa y direta."
    )
)

# 2. Agente especializado en razonamiento complejo
DeepThinkAgent = Agent(
    name="DeepThinkAgent",
    model="gemini-3.5-pro",
    instruction=(
        "Eres un asistente analítico experto. Responde problemas matemáticos, "
        "lógica, depuración de código o análisis profundos paso a paso."
    )
)

# 3. Agente Enrutador (Orquestador / Root)
root_agent = Agent(
    name="MyCustomRouter",
    model="gemini-3.5-flash", # Modelo rápido para clasificar
    instruction=(
        "Tu única tarea es analizar la solicitud del usuario y delegar al agente correcto:\n"
        "- Si es un saludo, conversación casual o pregunta simple, transfiere a FastTrackAgent.\n"
        "- Si involucra lógica compleja, matemáticas, programación o análisis profundo, transfiere a DeepThinkAgent."
    ),
    # Enlazamos los agentes a los que puede enrutar
    sub_agents=[FastTrackAgent, DeepThinkAgent] 
)

# Para correrlo en la web:
# adk web mi_archivo:MyCustomRouter
