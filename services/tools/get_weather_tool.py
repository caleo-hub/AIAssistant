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
        pass

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
            "city": city,
            "temperature": "25°C",
            "condition": "Ensolarado",
            "humidity": "60%",
            "wind_speed": "15 km/h",
        }

        return simulated_weather

    def get_tool_infos(self):
        """
        Retorna as informações da ferramenta, incluindo o tipo e os parâmetros esperados.

        :return: Dicionário com as informações da ferramenta.
        """
        return {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Retorna o clima de um cidade específica.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "Nome da cidade para a qual o clima será simulado.",
                        }
                    },
                    "required": ["city"],
                },
            },
        }

    def execute(self, city: str):
        """
        Executa a simulação de obtenção do clima para a cidade fornecida.

        :param city: Nome da cidade para a qual o clima será simulado.
        :return: Dados simulados do clima no formato de dicionário.
        """
        return self.get_weather(city=city)
