# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from google.adk.agents import Agent
from google.adk import Workflow
from google.adk import Event
from pydantic import BaseModel
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types
from google.adk.events import RequestInput
from typing import List, Dict

MODEL = "gemini-3.7-flash"

process_message = Agent(
    name="process_message",
    model="gemini-flash-latest",
    instruction="""Classify user message into either "BUG", "CUSTOMER_SUPPORT",
      or "LOGISTICS". If you think a message applies to more than one category,
      reply with a comma separated list of categories.
   """,
    output_schema=str,
)

def router(node_input: str):
    routes = node_input.split(",")
    routes = [route.strip() for route in routes]
    return Event(route=routes, output=routes)

def router_aprobacion(node_input: str):
    """
    Recibe la respuesta del usuario (node_input) desde el nodo 'aprobar'
    y define la ruta hacia donde debe fluir el grafo.
    """
    decision = node_input.strip().upper()
    
    # Manejamos las 3 opciones posibles
    if decision in ["APROBAR", "REVISAR", "ESCALAR"]:
        return Event(route=[decision])
        
    # En caso de una entrada no válida, se puede enviar a una ruta por defecto
    return Event(route=["REVISAR"]) 

def response_1_bug():
    return Event(message="Handling bug...", output="BUG")

def response_2_support():
    return Event(message="Handling customer support...", output="SUPPORT")

def response_3_logistics():
    return Event(message="Handling logistics...", output="LOGISTICS")

def response_4_aprobado():
    return Event(message="Approved...")

def response_5_revisar():
    return Event(message="Review...")

def response_6_escalar():
    return Event(message="Escalate...")

class ActivitiesList(BaseModel):
   """Itinerary should be a list of dictionaries for each activity. Each
   activity has a name and a description"""
   itinerary: List[Dict[str, str]]
   
def aprobar(node_input: str): # Human input step
   """
   Recibe el itinerario elegido y pide al usuario que lo apruebe
   El usuario debe responder o APROBAR o REVISAR o ESCALAR
   """

   message= (f"""
       Este es el itinerario recomendado:\n{node_input}\n\n)
       Aprobas el proceso (APROBAR, REVISAR, ESCALAR)?
       """
   )
   yield RequestInput(
       message=message,
       payload=node_input,
       response_schema=str,
   )

root_agent = Workflow(
   name="routing_workflow",
   edges=[
       ("START", process_message, router),
       ( router,
           {
               "BUG": response_1_bug,
               "CUSTOMER_SUPPORT": response_2_support,
               "LOGISTICS": response_3_logistics,
           }
       ),
       (response_1_bug, aprobar),
       (response_2_support, aprobar),
       (response_3_logistics, aprobar),
       (aprobar, router_aprobacion),
       (router_aprobacion,
           {
               "APROBAR": response_4_aprobado,
               "REVISAR": response_5_revisar,
               "ESCALAR": response_6_escalar,
           }
       ),
   ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
