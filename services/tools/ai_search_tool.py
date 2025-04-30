import os
from interfaces.tool_base import AssistantToolBase
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential


class AISearchTool(AssistantToolBase):
    """
    Classe para realizar buscas vetorizadas no Azure Cognitive Search.

    Esta classe utiliza as melhores práticas para autenticação e execução de buscas
    vetorizadas em um índice configurado no Azure Cognitive Search. Ela é projetada
    para ser usada como uma ferramenta auxiliar em assistentes baseados em IA.
    """

    def __init__(self):
        """
        Inicializa a classe AISearchTool carregando variáveis de ambiente,
        configurando o cliente de busca e definindo o campo vetorial.
        """
        self.campo_vetorial = "text_vector"  # Nome do campo vetorizado no índice

        self.api_key = os.getenv("AZURE_AI_SEARCH_API_KEY")
        self.endpoint = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
        self.ai_search_index = os.getenv("AZURE_AI_SEARCH_INDEX")

        self.credential = self._create_credential()
        self.client = self._create_search_client()

    def _create_credential(self):
        """
        Cria e retorna as credenciais para autenticação no Azure Cognitive Search.

        :return: Instância de AzureKeyCredential.
        """
        if not self.api_key:
            raise ValueError("AZURE_AI_SEARCH_API_KEY não configurada.")
        return AzureKeyCredential(self.api_key)

    def _create_search_client(self):
        """
        Cria e retorna o cliente de busca para o Azure Cognitive Search.

        :return: Instância de SearchClient.
        """
        if not self.endpoint or not self.ai_search_index:
            raise ValueError(
                "AZURE_AI_SEARCH_ENDPOINT ou AZURE_AI_SEARCH_INDEX não configurados."
            )
        return SearchClient(
            endpoint=self.endpoint,
            index_name=self.ai_search_index,
            credential=self.credential,
        )

    def ai_search_tool(self, **kwargs):
        """
        Realiza uma busca vetorizada no índice configurado no Azure Cognitive Search.

        :param kwargs: Parâmetros opcionais, incluindo:
            - prompt (str): Texto a ser pesquisado.
            - k_results (int): Número de resultados a serem retornados (padrão: 3).
        :return: Lista de tuplas contendo os resultados no formato:
            (chunk, title, metadata_storage_path).
        """
        prompt = kwargs.get("prompt", "")
        k_results = kwargs.get("k_results", 3)

        # 🔍 Realiza a busca vetorizada
        results = self.client.search(
            vector_queries=[
                {
                    "kind": "text",  # ou "vector" se você quiser passar o vetor manualmente
                    "text": prompt,
                    "fields": self.campo_vetorial,
                    "k": k_results,
                }
            ],
            top=k_results,
            select=[
                "chunk",
                "title",
                "metadata_storage_path",
            ],  # Campos que deseja retornar
        )

        # 📦 Processa os resultados
        return self._process_results(results)

    def _process_results(self, results):
        """
        Processa os resultados da busca e os formata como uma lista de tuplas.

        :param results: Resultados retornados pelo cliente de busca.
        :return: Lista de tuplas no formato (chunk, title, metadata_storage_path).
        """
        return [
            (
                result.get("chunk", "")[:300],  # Limita o chunk a 300 caracteres
                result.get("title", "sem título"),
                result.get("metadata_storage_path", "sem nome"),
            )
            for result in results
        ]

    def get_tool_infos(self):
        """
        Retorna as informações da ferramenta, incluindo o tipo e os parâmetros esperados.

        :return: Dicionário com as informações da ferramenta.
        """
        return {
            "type": "function",
            "function": {
                "name": "ai_search_tool",
                "description": "Data source para RAG do chatbot",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "O prompt do usuário",
                        }
                    },
                    "required": ["prompt"],
                },
            },
        }

    def execute(self, prompt: str, k_results: int = 3):
        """
        Executa a busca vetorizada com os parâmetros fornecidos.

        :param prompt: Texto a ser pesquisado.
        :param k_results: Número de resultados a serem retornados (padrão: 3).
        :return: Resultados da busca no formato de lista de tuplas.
        """
        return self.ai_search_tool(prompt=prompt, k_results=k_results)
