from google.adk.agents.llm_agent import Agent

from .stock_agent.agent import stock_agent
from .info_agent.agent import info_agent
from .order_agent.agent import order_agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='Un agente para vender productos.',
    instruction=f'''Sos un agente que vende productos. Tenes que determinar que producto quiere el cliente y en que cantidad.
    Antes de confirmar la venta tenes que asegurarte si hay stock de ese producto con el agente "stock_agent". Si el stock es 0 o es menor a la cantidad que quiere comprar entonces debes informarle que no puede comprar porque no hay stock.
    No debes confirmar la compra sin haber validado el stock.
    Una vez confirmada la venta tenes que crear la orden con el agente "order_agent" e informarle al cliente el nro de orden de compra.
    Si te pide el cliente informacion de un producto o el precio, se la podes brindar con el agente "info_agent".''',
    sub_agents=[stock_agent, info_agent, order_agent]
)
