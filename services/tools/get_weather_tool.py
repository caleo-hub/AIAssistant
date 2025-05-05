import time
from interfaces.tool_base import AssistantToolBase


class WeatherSimulationTool(AssistantToolBase):
    """
    Classe para simular a obtenção do clima de uma cidade.

    Esta classe simula a consulta de informações climáticas para uma cidade
    fornecida como entrada, com um atraso para imitar o tempo de resposta de uma API real.
    """

    def __init__(self):
        """
        Inicializa a classe WeatherSimulationTool.
        """
        # Variáveis do dicionário get_tool_infos
        self.tool_type = "function"
        self.tool_name = "get_weather"
        self.tool_description = "Retorna o clima de um cidade específica."
        self.tool_parameters = {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Nome da cidade para a qual o clima será simulado.",
                }
            },
            "required": ["city"],
        }

    def get_weather(self, city: str):
        """
        Simula a obtenção do clima para uma cidade específica.

        :param city: Nome da cidade para a qual o clima será simulado.
        :return: Dicionário contendo informações simuladas do clima.
        """
        # Simula um atraso para imitar o tempo de resposta de uma API real
        time.sleep(2)

        # Dados climáticos simulados
        simulated_weather = {
            "tool_output": {
                "city": city,
                "temperature": "25°C",
                "condition": "Ensolarado",
                "humidity": "60%",
                "wind_speed": "15 km/h",
            }
        }

        return simulated_weather

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

    def execute(self, city: str):
        """
        Executa a simulação de obtenção do clima para a cidade fornecida.

        :param city: Nome da cidade para a qual o clima será simulado.
        :return: Dados simulados do clima no formato de dicionário.
        """
        return self.get_weather(city=city)
