Tener en cuenta que por los ultimos cambios de ADK, cuando prueba adk web desde el Cloud Shell tengo que ejecutarlo:

adk web --allow_origins "regex:https://.*\.cloudshell\.dev"

Y si lo pruebo desde Cloud Workstations:

adk web --allow_origins "regex:https://.*\.cloudworkstations\.dev"