from google.adk.agents.llm_agent import Agent

from .info_agent.agent import info_agent
from .order_agent.agent import order_agent


class GoogleCloudAuth(httpx.Auth):
    """Auto-refreshing Google Cloud authentication for httpx.

    Refreshes the access token before each request if expired,
    so long-running agents never hit 401 errors.
    """

    def __init__(self):
        self.credentials, _ = default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

    def auth_flow(self, request):
        # Refresh the token if it is expired or missing
        if not self.credentials.valid:
            self.credentials.refresh(AuthRequest())
            
        request.headers["Authorization"] = f"Bearer {self.credentials.token}"
        yield request


reservation_remote_agent = RemoteA2aAgent(
    name="reservation_agent",
    description="Handles restaurant table reservations — create, check, and cancel bookings. Delegate to this agent when the user wants to book a table, check a reservation, or cancel a reservation.",
    agent_card=RESERVATION_AGENT_CARD_URL,
    httpx_client=httpx.AsyncClient(auth=GoogleCloudAuth(), timeout=60),
)
# Configurar el Cliente del Agente Remoto
# RemoteA2aAgent es el componente del lado del cliente que sabe cómo hablar con
# un servidor A2A. Lo configuramos con la URL de nuestro math_agent.
stock_agent = RemoteA2aAgent(
    name="stock_agent",
    description="Un agente que valida el stock de los productos.",
    agent_card=(
        f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}"
    ),
)

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
