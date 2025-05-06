import os
import time
import requests
from interfaces.tool_base import AssistantToolBase

class GetIncidentStatusTool(AssistantToolBase):
    """
    Classe para buscar informações de um incidente no ServiceNow
    com base no número do incidente fornecido pelo usuário.
    """

    def __init__(self):
        """
        Inicializa a classe GetIncidentStatusTool.
        """
        # Configurações da API (pode passar por environment vars)
        self.instance_url = os.getenv("SN_INSTANCE_URL")
        self.user = os.getenv("SN_USER")
        self.pwd = os.getenv("SN_PWD")
        
        # Configurações do tool_info
        self.tool_type = "function"
        self.tool_name = "get_incident_status"
        self.tool_description = (
            "Busca o status e detalhes de um incidente do ServiceNow "
            "usando a Table API e o número do incidente."
        )
        self.tool_parameters = {
            "type": "object",
            "properties": {
                "incident_number": {
                    "type": "string",
                    "description": "Número do incidente.",
                    "pattern": "^INC\\d{8}$",
                }
            },
            "required": ["incident_number"],
        }

    def get_tool_infos(self):
        """
        Retorna as informações da ferramenta, incluindo o tipo e os parâmetros esperados.
        """
        return {
            "type": self.tool_type,
            "function": {
                "name": self.tool_name,
                "description": self.tool_description,
                "parameters": self.tool_parameters,
            },
        }

    def get_incident_status(self, incident_number: str):
        """
        Realiza chamada HTTP à ServiceNow Table API para buscar o incidente.
        """
        # Monta URL e parâmetros de consulta
        url = f"{self.instance_url}/api/now/table/u_mock_incident"
        params = {
            "sysparm_query": f"number={incident_number}",
            "sysparm_limit": 1
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Faz a requisição
        response = requests.get(url, auth=(self.user, self.pwd), headers=headers, params=params)
        if response.status_code != 200:
            return {"tool_output": {
                "error": f"Falha na requisição ({response.status_code}): {response.text}"
            }}

        result = response.json().get("result", [])
        if not result:
            return {"tool_output": {
                "message": f"Nenhum incidente encontrado com o número {incident_number}."
            }}

        # Retorna o primeiro registro encontrado
        record = result[0]
        return {"tool_output": record}

    def execute(self, **kwargs):
        """
        Entry-point para o tool: valida e dispara a busca.
        """
        incident_number = kwargs.get("incident_number")
        if not incident_number:
            return {
                "tool_output": {
                    "error": "Por favor, informe o número do incidente."
                }
            }
        return self.get_incident_status(incident_number=incident_number)

