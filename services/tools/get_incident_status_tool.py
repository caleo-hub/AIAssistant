import time
from interfaces.tool_base import AssistantToolBase


class GetIncidentStatusTool(AssistantToolBase):
    """
    Classe para simular a obtenção de informações de um incidente no ServiceNow
    com base no número do incidente fornecido pelo usuário.
    """

    def __init__(self):
        """
        Inicializa a classe GetIncidentStatusTool.
        """
        # Variáveis do dicionário get_tool_infos
        self.tool_type = "function"
        self.tool_name = "get_incident_status"
        self.tool_description = (
            "Simula a obtenção do status e detalhes de um incidente do ServiceNow "
            "com base no número do incidente fornecido."
        )
        self.tool_parameters = {
            "type": "object",
            "properties": {
                "incident_number": {
                    "type": "string",
                    "description": "Número do incidente para o qual as informações serão simuladas. Deve estar no formato INC seguido de 8 dígitos",
                    "pattern": "^INC\\d{8}$",
                },
                "is_valid": {
                    "type": "boolean",
                    "description": "Indica se o número do incidente está no formato correto (true) ou incorreto (false).",
                },
            },
            "required": ["incident_number", "is_valid"],
        }

    def get_incident_status(self, incident_number: str, is_valid: bool):
        """
        Simula a obtenção de informações de um incidente no ServiceNow.

        :param incident_number: Número do incidente fornecido pelo usuário.
        :param is_valid: Indica se o número do incidente está no formato correto.
        :return: Dicionário contendo informações simuladas do incidente ou mensagem de erro.
        """
        if not is_valid:
            return {
                "tool_output": {
                    "error": "O número do incidente foi digitado incorretamente. Verifique o formato e tente novamente."
                }
            }

        # Simula um atraso para imitar o tempo de resposta de uma API real
        time.sleep(2)

        # Resposta simulada para demonstração
        simulated_response = {
            "tool_output": {
                "incident_number": incident_number,
                "status": "Resolved",
                "priority": "High",
                "assigned_to": "John Doe",
                "short_description": "System outage affecting multiple users",
                "resolution_notes": "Issue resolved by restarting the affected services.",
            }
        }

        return simulated_response

    def get_tool_infos(self):
        """
        Retorna as informações da ferramenta, incluindo o tipo e os parâmetros esperados.

        :return: Dicionário com as informações da ferramenta.
        """
        return {
            "type": self.tool_type,
            "function": {
                "name": self.tool_name,
                "description": self.tool_description,
                "parameters": self.tool_parameters,
            },
        }

    def execute(self, **kwargs):
        """
        Executa a simulação de obtenção de informações de um incidente.

        :param incident_number: Número do incidente fornecido pelo usuário.
        :param is_valid: Indica se o número do incidente está no formato correto.
        :return: Dados simulados do incidente no formato de dicionário ou mensagem de erro.
        """
        incident_number = kwargs.get("incident_number")
        is_valid = kwargs.get("is_valid")
        if not incident_number:
            return {
                "tool_output": "Incidente não identificado. Poderia digitar novamente o número do incidente?"
            }
        return self.get_incident_status(
            incident_number=incident_number, is_valid=is_valid
        )
